# %%
import marEx
import numpy as np
import xarray as xr

from vosse.analysis.params import FPaths

# %%

marEx_tracked: xr.Dataset = xr.open_dataset(FPaths.marEx_tracked)
marEx_tracked = marEx_tracked.rename({"latitude": "lat", "longitude": "lon"})

merged_events: xr.Dataset = xr.open_dataset(FPaths.marEx_merged)

# %%

# Build a merged ID_field where all events in the same merge group share a single ID,
# so they are painted as one big blob when plotted.
#
# merge_ledger dims: (time, ID, sibling_ID)
# For each (time, ID), the sibling_ID axis lists the IDs of other events that are
# currently merged with it (0 = no sibling).  We assign every sibling in a group
# the minimum ID in that group so they all receive the same colour.

june_slice = slice("2023-06-01", "2023-06-30")

june_id_field = marEx_tracked.ID_field.sel(time=june_slice).compute()
june_ledger = marEx_tracked.merge_ledger.sel(time=june_slice).compute()

# For each (time, ID): minimum sibling ID, ignoring zeros
min_sibling = june_ledger.where(june_ledger > 0).min(dim="sibling_ID")  # (time, ID)

# Representative = min(own ID, min sibling).  Falls back to own ID when no siblings.
id_coord = xr.DataArray(june_ledger.ID.values, dims="ID")
representative = xr.where(
    min_sibling.notnull(),
    np.minimum(min_sibling, id_coord),
    id_coord,
).astype(np.int32)  # (time, ID)

# _id_values: the actual integer event-ID values on the ID coordinate axis
_id_values = june_ledger.ID.values.astype(np.int32)


def _remap_field(field: np.ndarray, reps: np.ndarray) -> np.ndarray:
    """Remap one (lat, lon) slice using the representative-ID lookup for that timestep.

    field : (lat, lon) int32  — original ID_field for one timestep
    reps  : (N_IDs,)  int32  — representative ID for each entry in _id_values
    """
    max_id = int(_id_values.max()) if len(_id_values) > 0 else 0
    # Build a lookup array indexed by event-ID value (identity by default)
    lookup = np.arange(max_id + 1, dtype=np.int32)
    valid = (_id_values > 0) & (_id_values <= max_id)
    lookup[_id_values[valid]] = reps[valid]
    # Apply lookup (clip to guard against any IDs outside the expected range)
    return lookup[np.clip(field, 0, max_id)]


june2023_events: xr.DataArray = xr.apply_ufunc(
    _remap_field,
    june_id_field,
    representative,
    input_core_dims=[["lat", "lon"], ["ID"]],
    output_core_dims=[["lat", "lon"]],
    vectorize=True,  # _remap_field is called once per time step
    dask="parallelized",
    output_dtypes=[np.int32],
)


# %%

# quick timeseries/map plot (maps per day of June 2023)

config = marEx.PlotConfig(plot_IDs=True)
fig, ax = june2023_events.plotX.multi_plot(config, col="time", col_wrap=3)


# %%

# animation of June 2023
# config = marEx.PlotConfig(plot_IDs=True)
# june2023_events.plotX.animate(config, plot_dir=FPaths.plot_dir, file_name="june2023_events")
