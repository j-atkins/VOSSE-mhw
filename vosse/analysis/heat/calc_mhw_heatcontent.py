# %%

import os

import copernicusmarine
from dask.diagnostics import ProgressBar
from dask.distributed import Client
import xarray as xr

from vosse.analysis.params import FPaths, HeatContentParams, TrackingParams
from vosse.utils import get_area_weights

# %%

tracked_ds = xr.open_dataset(FPaths.marEx_tracked, chunks={})

extra_copernicus_params = {
    "start_datetime": HeatContentParams.start_date,
    "end_datetime": HeatContentParams.end_date,
    "coordinates_selection_method": "outside",
    "minimum_longitude": HeatContentParams.lon_min,
    "maximum_longitude": HeatContentParams.lon_max,
    "minimum_latitude": HeatContentParams.lat_min,
    "maximum_latitude": HeatContentParams.lat_max,
}

if TrackingParams.method_anomaly == "shifting_baseline":
    tracked_tslice = slice(
        tracked_ds.time.min().values, tracked_ds.time.max().values
    )  # factoring in that shifting baseline method for anomalies means N years are removed from timeseries
else:
    tracked_tslice = slice(None)  # No slicing for other methods


thetao_ds = (
    copernicusmarine.open_dataset(
        dataset_id=HeatContentParams.product_id, variables=["thetao"], **extra_copernicus_params
    )
    .sel(time=tracked_tslice)
    .chunk({"time": 30, "latitude": -1, "longitude": -1})
)

mld_ds = (
    copernicusmarine.open_dataset(
        dataset_id=HeatContentParams.mld_id, variables=["mlotst"], **extra_copernicus_params
    )
    .sel(time=tracked_tslice)
    .chunk({"time": 30, "latitude": -1, "longitude": -1})
)

# %%


# TODO: add area weighting to calcualtions!
# TODO: probs via a utils function


def calc_heat_content(tracked_ds: xr.Dataset, thetao_ds: xr.Dataset, mld_ds: xr.Dataset):
    """
    Calculate heat content for each event, in the mixed layer.

    Takes events tracked via marEx and original temperature data (full depth) to calculate heat content within the mixed layer per event.
    """

    RHO = 1026  # kg/m^3; density of seawater
    C_P = 3990  # J/(kg K); specific heat capacity of seawater

    ID_field = tracked_ds.ID_field
    IDs = xr.DataArray(tracked_ds.ID).chunk(
        chunks={"ID": 200}
    )  # N.B.: The intermediate arrays would get too large without this ID chunk

    # event mask with dimensions
    event_mask = ID_field == IDs

    # mld mask (True where depth is within the mixed layer, False below)
    mld_mask = thetao_ds.depth <= mld_ds.mlotst

    breakpoint()

    # masked temperature data
    temp = thetao_ds.where(mld_mask)  # by within mixed layer
    temp = temp.where(event_mask)  # by within event

    # area weighting (cosine of latitude)
    area_weights = get_area_weights(temp)
    temp = temp.weighted(area_weights)

    # weight temperature by delta depths
    delta_level = abs(thetao_ds.depth[:, 1] - thetao_ds.depth[:, 0])  # TODO: check this
    weighted_temp = temp * delta_level

    # calculate heat content
    heat_content = RHO * C_P * weighted_temp.sum(dim="depth")

    # Mask where the event isn't present
    heat_content = heat_content.where(tracked_ds.presence)

    return heat_content


# %%

# run calculations

Cl = Client(processes=False)

with Cl as client:
    print(f"Dask Dashboard available at: {client.dashboard_link}")

    heat_content = calc_heat_content(tracked_ds, thetao_ds, mld_ds)

    os.makedirs(FPaths.mhw_heat_content, exist_ok=True)
    with ProgressBar():
        heat_content.to_zarr(FPaths.mhw_heat_content, consolidated=True)

    client.close()
