import copernicusmarine
import numpy as np
import xarray as xr

from vosse.analysis.params import TrackingParams


def get_area_weights(ds: xr.Dataset) -> xr.DataArray:
    latrad = np.deg2rad(ds.latitude)
    return np.cos(latrad)


def get_bathymetry_ds(
    lon_min=TrackingParams.lon_min,
    lon_max=TrackingParams.lon_max,
    lat_min=TrackingParams.lat_min,
    lat_max=TrackingParams.lat_max,
):
    """Get the bathymetry dataset (and load to memory)."""

    return copernicusmarine.open_dataset(
        dataset_id=TrackingParams.bathy_id,
        coordinates_selection_method="outside",
        minimum_longitude=lon_min,
        maximum_longitude=lon_max,
        minimum_latitude=lat_min,
        maximum_latitude=lat_max,
    ).load()


def make_ocean_mask(
    lon_min=TrackingParams.lon_min,
    lon_max=TrackingParams.lon_max,
    lat_min=TrackingParams.lat_min,
    lat_max=TrackingParams.lat_max,
):
    """
    Make a land/ocean mask from bathymetry dataset.

    N.B. ocean points are 1, land points are 0. This is the convention used by ocetrac.
    As opposed to a typical land mask.

    """

    bathy = get_bathymetry_ds(lon_min, lon_max, lat_min, lat_max).deptho
    mask = xr.where(bathy >= 0, 1, 0)  # land/sea mask

    return mask
