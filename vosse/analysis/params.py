from dataclasses import dataclass

from vosse.config import PROCESSED_DATA_DIR


@dataclass
class FPaths:
    """Local file paths."""

    # MHW detection & tracking [ocetrac version]
    ocetrac_anomalies: str = f"{PROCESSED_DATA_DIR}/ocetrac_track/anomalies.zarr"
    ocetrac_blobs: str = f"{PROCESSED_DATA_DIR}/ocetrac_track/blobs.zarr"

    # MHW tracking [marEx version]
    marEx_detected: str = f"{PROCESSED_DATA_DIR}/marEx_track/extremes.zarr"
    marEx_tracked: str = f"{PROCESSED_DATA_DIR}/marEx_track/tracked_events.zarr"
    marEx_merged: str = f"{PROCESSED_DATA_DIR}/marEx_track/merge_events.zarr"

    # plots
    plot_dir: str = f"{PROCESSED_DATA_DIR}/plots"


@dataclass
class TrackingParams:
    """Parameters for MHW tracking."""

    product_id: str = (
        "cmems_mod_nws_phy-t_my_7km-3D_P1D-m"  # NWS product, physics, AMM7 (7km), daily, global
    )

    bathy_id: str = "cmems_mod_nws_phy_my_7km-3D_static"

    start_date: str = "1993-01-01"
    end_date: str = "2026-04-01"

    # 'zoom in' on the shelf region (i.e. < 200m depth area); mainly just to speed up tracking
    lat_min: float = 47.0
    lat_max: float = 63.0
    lon_min: float = -14.4
    lon_max: float = 10.0

    # tracking parameters
    ocetrac_in_memory = True
    ocetrac_threshold = 0.90  # percentile threshold for ocetrac (percentile)
