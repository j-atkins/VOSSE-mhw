from dataclasses import dataclass

from vosse.config import PROCESSED_DATA_DIR


@dataclass
class FPaths:
    """Local file paths."""

    detected_extremes: str = f"{PROCESSED_DATA_DIR}/marEx_track/extremes.zarr"
    tracked_events: str = f"{PROCESSED_DATA_DIR}/marEx_track/tracked_events.zarr"
    merge_events: str = f"{PROCESSED_DATA_DIR}/marEx_track/merge_events.zarr"


@dataclass
class TrackingParams:
    """Parameters for MHW tracking."""

    product_id: str = (
        "cmems_mod_nws_phy-t_my_7km-3D_P1D-m"  # NWS product, physics, AMM7 (7km), daily, global
    )

    start_date: str = "1993-01-01"
    end_date: str = "2026-01-01"

    # 'zoom in' on the shelf region (i.e. < 200m depth area); mainly just to speed up tracking
    lat_min: float = 47.0
    lat_max: float = 63.0
    lon_min: float = -14.4
    lon_max: float = 10.0
