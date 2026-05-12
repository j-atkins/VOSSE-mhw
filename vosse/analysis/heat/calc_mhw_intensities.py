# %%

import os

from dask.diagnostics import ProgressBar
from dask.distributed import Client
import xarray as xr

from vosse.analysis.params import FPaths
from vosse.utils import get_area_weights

# %%

tracked_ds = xr.open_dataset(FPaths.marEx_tracked, chunks={})
anomalies_ds = xr.open_dataset(FPaths.marEx_detected, chunks={})

# %%

# TODO: add area weighting to calcualtions!
# TODO: probs via a utils function


def calc_intensities(tracked_ds: xr.Dataset, anomalies_ds: xr.Dataset):
    """
    Compose MHW intensity stats per event.

    statistic post-processing guidance gratefully received from `wiekners` (developer) on the marEx GitHub discussions (https://github.com/wienkers/marEx/discussions/4)
    """

    # anomaly data (+ area weighting)
    anomaly = anomalies_ds.dat_anomaly
    area_weights = get_area_weights(anomaly)
    anomaly = anomaly.weighted(area_weights)

    ID_field = tracked_ds.ID_field
    IDs = xr.DataArray(tracked_ds.ID).chunk(
        chunks={"ID": 200}
    )  # N.B.: The intermediate arrays would get too large without this ID chunk

    # Boolean mask with dimensions (time, lat, lon, ID)
    event_mask = ID_field == IDs

    # Resulting DataArrays are (time, ID)
    mean_intensity = anomaly.where(event_mask).mean(dim=["latitude", "longitude"])
    peak_intensity = anomaly.where(event_mask).max(dim=["latitude", "longitude"])

    # Mask where the event isn't present
    mean_intensity = mean_intensity.where(tracked_ds.presence)
    peak_intensity = peak_intensity.where(tracked_ds.presence)

    return mean_intensity, peak_intensity


# %%

## INTENSITIES

Cl = Client(processes=False)

with Cl as client:
    print(f"Dask Dashboard available at: {client.dashboard_link}")

    mean_intensity, peak_intensity = calc_intensities(tracked_ds, anomalies_ds)

    os.makedirs(FPaths.mhw_mean_intensity, exist_ok=True)
    with ProgressBar():
        mean_intensity.to_zarr(FPaths.mhw_mean_intensity, consolidated=True)
        peak_intensity.to_zarr(FPaths.mhw_peak_intensity, consolidated=True)

    client.close()

# %%
