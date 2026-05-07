# %%

import copernicusmarine
import xarray as xr

from vosse.analysis.params import FPaths, HeatContentParams

# %%

tracked_ds = xr.open_dataset(FPaths.marEx_tracked, chunks={})

thetao_ds = copernicusmarine.open_dataset(
    dataset_id=HeatContentParams.product_id,
    variables=["thetao"],
    start_datetime=HeatContentParams.start_date,
    end_datetime=HeatContentParams.end_date,
    coordinates_selection_method="outside",
    minimum_longitude=HeatContentParams.lon_min,
    maximum_longitude=HeatContentParams.lon_max,
    minimum_latitude=HeatContentParams.lat_min,
    maximum_latitude=HeatContentParams.lat_max,
).chunk({"time": 25, "depth": -1, "latitude": -1, "longitude": -1})


# %%


def calc_heat_content(tracked_ds: xr.Dataset, thetao_ds: xr.Dataset) -> None:
    """
    Calculate heat content for each event.

    Takes events tracked via marEx and original temperature data (full depth) to calculate heat content per event.

    """
