"""
Tests for vosse.analysis.params

Ensures that parameter classes remain consistent with each other where
divergence is likely to be unintentional (e.g. HeatContentParams vs TrackingParams).
"""

import pytest

from vosse.analysis.params import HeatContentParams, TrackingParams

# Fields that must stay synchronised between HeatContentParams and TrackingParams
# unless explicitly diverged for a scientific reason.
SHARED_FIELDS = {
    "product_id",
    "start_date",
    "end_date",
    "lat_min",
    "lat_max",
    "lon_min",
    "lon_max",
}


@pytest.mark.parametrize("field", sorted(SHARED_FIELDS))
def test_heat_content_params_consistent_with_tracking_params(field):
    """Each shared field in HeatContentParams should match TrackingParams.

    If divergence is intentional, remove the field from SHARED_FIELDS above
    and add a comment explaining why.
    """
    tracking_value = getattr(TrackingParams, field)
    heat_content_value = getattr(HeatContentParams, field)
    assert heat_content_value == tracking_value, (
        f"HeatContentParams.{field} ({heat_content_value!r}) diverges from "
        f"TrackingParams.{field} ({tracking_value!r}). "
        "If intentional, remove this field from SHARED_FIELDS in tests/analysis/test_params.py."
    )
