# %%
import logging
import os

import copernicusmarine
from dask.diagnostics import ProgressBar
import numpy as np
import ocetrac
import xarray as xr

from vosse.analysis.params import FPaths, TrackingParams
from vosse.utils import make_ocean_mask

# ignore INFO messages from copernicusmarine
logging.getLogger("copernicusmarine").setLevel(logging.WARNING)


COPERNICUS_CREDS_FILE = os.path.expandvars("$HOME/.copernicusmarine/.copernicusmarine-credentials")

if os.path.isfile(COPERNICUS_CREDS_FILE) and os.path.getsize(COPERNICUS_CREDS_FILE) > 0:
    pass
else:
    print(
        "\nPlease enter your log in details for the Copernicus Marine Service (only necessary the first time you run this script). \n\nIf you have not registered yet, please do so at https://marine.copernicus.eu/.\n\n"
    )
    copernicusmarine.login()

# %%

## LOAD DATA

# type annotation just for readability

# land/shelf mask (via bathymetry file)
mask: xr.DataArray = make_ocean_mask()

# sst data
sst_ds: xr.Dataset = (
    copernicusmarine.open_dataset(
        dataset_id=TrackingParams.product_id,
        variables=["thetao"],
        start_datetime=TrackingParams.start_date,
        end_datetime=TrackingParams.end_date,
        coordinates_selection_method="outside",
        minimum_longitude=TrackingParams.lon_min,
        maximum_longitude=TrackingParams.lon_max,
        minimum_latitude=TrackingParams.lat_min,
        maximum_latitude=TrackingParams.lat_max,
    )
    .isel(depth=0)
    .chunk({"time": 25, "latitude": -1, "longitude": -1})
)

# mask land
sst_mask: xr.Dataset = sst_ds.where(
    ~mask, np.nan
)  # ~/bitwise 'not' operator to mask land with NaNs

# to dataarray
sst: xr.DataArray = sst_mask.thetao

# %%

## PRE-PROCESSING

# TODO: think about the climatological period... this is just all years... moving baseline?
# TODO: not super important for the purposes of this work though...

if not os.path.exists(FPaths.ocetrac_anomalies):
    climatology = sst.groupby(sst.time.dt.month).mean()
    anomaly = sst.groupby(sst.time.dt.month) - climatology

    if sst.chunks:
        sst = sst.chunk({"time": -1})

    percentile = TrackingParams.ocetrac_threshold
    threshold = sst.groupby(sst.time.dt.month).quantile(
        percentile, dim="time", keep_attrs=True, skipna=True
    )
    extremes = anomaly.groupby(anomaly.time.dt.month).where(
        sst.groupby(sst.time.dt.month) > threshold
    )

    os.makedirs(os.path.dirname(FPaths.ocetrac_anomalies), exist_ok=True)
    with ProgressBar():
        extremes.to_dataset(name="mhws").to_zarr(FPaths.ocetrac_anomalies, consolidated=True)

chunk_size = {"time": -1, "latitude": -1, "longitude": -1}  # modify if memory issues...
extremes_ds = xr.open_dataset(FPaths.ocetrac_anomalies, chunks=chunk_size)
extremes: xr.DataArray = extremes_ds.mhws

# to memory (can get away with this for the right region and computer specs!)
if TrackingParams.ocetrac_in_memory:
    extremes = extremes.compute()

# %%

## TRACKING

# force binaries
extremes_binary = (extremes > 0).compute()
ocean_mask = (mask > 0).compute()

# tracker
tracker = ocetrac.Tracker(
    extremes_binary,
    ocean_mask,
    radius=1,  # morphological structuring element radius
    min_size_quartile=0.2,  # keep objects larger than the 75th-percentile area
    timedim="time",
    xdim="longitude",
    ydim="latitude",
    positive=True,  # detect positive (warm) anomalies
)

blobs = tracker.track()

blobs.to_dataset(name="blobs").to_zarr(FPaths.ocetrac_blobs, consolidated=True)
