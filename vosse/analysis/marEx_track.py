# %%
import os

import copernicusmarine
from dask.distributed import Client
import marEx
import xarray as xr

from vosse.analysis.params import FPaths, TrackingParams

# %%
COPERNICUS_CREDS_FILE = os.path.expandvars("$HOME/.copernicusmarine/.copernicusmarine-credentials")

if os.path.isfile(COPERNICUS_CREDS_FILE) and os.path.getsize(COPERNICUS_CREDS_FILE) > 0:
    pass
else:
    print(
        "\nPlease enter your log in details for the Copernicus Marine Service (only necessary the first time you run this script). \n\nIf you have not registered yet, please do so at https://marine.copernicus.eu/.\n\n"
    )
    copernicusmarine.login()

# %%

sst_ds = (
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


# %%

# detect extremes (save or load to/from disk if already exists)

## this may take a while; depending on internet connection etc... but no downloads required so that's fun!

if not os.path.exists(FPaths.detected_extremes):
    extremes = marEx.preprocess_data(
        sst_ds.thetao,
        dimensions={"time": "time", "y": "latitude", "x": "longitude"},
        method_anomaly="shifting_baseline",  # Anomalies from a rolling climatology using previous window_year years
        method_extreme="hobday_extreme",  # Local day-of-year specific thresholds with windowing
        threshold_percentile=95,  # 95th percentile threshold for extremes
        window_year_baseline=15,  # Rolling climatology window
        smooth_days_baseline=21,  #    and smoothing window [days] for determining the anomalies
        window_days_hobday=11,  # Window size of compiled samples collected for the extremes detection
        verbose=True,
    )

    os.makedirs(FPaths.detected_extremes, exist_ok=True)
    extremes.to_zarr(FPaths.detected_extremes, consolidated=True)

chunk_size = {"time": 25, "lat": -1, "lon": -1}
extremes = xr.open_dataset(FPaths.detected_extremes, chunks=chunk_size)

# %%


def main():
    client = Client()
    print(f"Dask Dashboard available at: {client.dashboard_link}")

    with Client() as client:
        print("Tracking started...")

        # ID, Track, & Merge
        tracked_events, merge_events = marEx.tracker(
            extremes.extreme_events,
            extremes.mask,
            area_filter_absolute=100,  # Remove objects smaller than 100 grid cells
            R_fill=8,  # Radius for filling gaps (in grid cells)
            dimensions={"time": "time", "y": "latitude", "x": "longitude"},
            regional_mode=True,
            coordinate_units="degrees",
            verbose=False,
        ).run(return_merges=True)

        tracked_events.to_zarr(FPaths.tracked_events, consolidated=True)
        merge_events.to_zarr(FPaths.merge_events, consolidated=True)

        print("Tracking complete and results saved to disk.")


if __name__ == "__main__":
    main()

# %%
