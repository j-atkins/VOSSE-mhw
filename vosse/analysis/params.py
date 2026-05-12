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

    # post-processed MHW stats
    mhw_mean_intensity: str = f"{PROCESSED_DATA_DIR}/mhw_stats/mean_intensity.zarr"
    mhw_peak_intensity: str = f"{PROCESSED_DATA_DIR}/mhw_stats/peak_intensity.zarr"
    mhw_heat_content: str = f"{PROCESSED_DATA_DIR}/mhw_stats/heat_content.zarr"

    # plots
    plot_dir: str = f"{PROCESSED_DATA_DIR}/plots"


@dataclass
class TrackingParams:
    """Parameters for MHW tracking."""

    # products
    product_id: str = "cmems_mod_glo_phy_my_0.083deg_P1D-m"  # Global physics reanalysis product
    bathy_id: str = "cmems_mod_glo_phy_my_0.083deg_static"  # "

    # anomaly detection parameters
    method_anomaly: str = "shifting_baseline"  # anomalies from a rolling climatology

    # time bounds
    start_date: str = "1993-01-01"
    end_date: str = "2026-01-01"

    # 'zoom in' on the shelf region (i.e. < 200m depth area); mainly just to speed up tracking
    lat_min: float = 47.0
    lat_max: float = 63.0
    lon_min: float = -14.4
    lon_max: float = 10.0


@dataclass
class HeatContentParams:
    """Parameters for heat content calculation."""

    product_id: str = "cmems_mod_glo_phy_my_0.083deg_P1D-m"  # Global physics reanalysis product
    mld_id: str = "cmems_mod_glo_phy_my_0.083deg_P1D-m"  # "

    start_date: str = "1993-01-01"
    end_date: str = "2026-01-01"

    # 'zoom in' on the shelf region (i.e. < 200m depth area); mainly just to speed up tracking
    lat_min: float = 47.0
    lat_max: float = 63.0
    lon_min: float = -14.4
    lon_max: float = 10.0
