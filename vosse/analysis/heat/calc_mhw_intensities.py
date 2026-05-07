# %%

import os

from dask.distributed import Client
import xarray as xr

from vosse.analysis.params import FPaths

# %%

tracked_ds = xr.open_dataset(FPaths.marEx_tracked, chunks={})
anomalies_ds = xr.open_dataset(FPaths.marEx_detected, chunks={})

# %%


def calc_intensities(tracked_ds: xr.Dataset, anomalies_ds: xr.Dataset) -> None:
    """
    Compose MHW intensity stats per event.

    statistic post-processing guidance gratefully received from `wiekners` (developer) on the marEx GitHub discussions (https://github.com/wienkers/marEx/discussions/4)
    """

    anomaly = anomalies_ds.dat_anomaly
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
    mean_intensity = mean_intensity.where(tracked_ds.presence).compute()
    peak_intensity = peak_intensity.where(tracked_ds.presence).compute()

    return mean_intensity, peak_intensity


# %%

## INTENSITIES

Cl = Client(processes=False)

with Cl as client:
    print(f"Dask Dashboard available at: {client.dashboard_link}")

    mean_intensity, peak_intensity = calc_intensities(tracked_ds, anomalies_ds)

    client.close()

os.makedirs(FPaths.mhw_mean_intensity, exist_ok=True)
mean_intensity.to_zarr(FPaths.mhw_mean_intensity, consolidated=True)
peak_intensity.to_zarr(FPaths.mhw_peak_intensity, consolidated=True)

# %%
