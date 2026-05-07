# %%
import marEx
import xarray as xr

from vosse.analysis.params import FPaths

# %%

marEx_tracked: xr.Dataset = xr.open_dataset(FPaths.marEx_tracked)
marEx_tracked = marEx_tracked.rename({"latitude": "lat", "longitude": "lon"})

merged_events: xr.Dataset = xr.open_dataset(FPaths.marEx_merged)

# %%

june_slice = slice("2023-06-01", "2023-07-01")
june2023_events = marEx_tracked.sel(time=june_slice)

# %%

# quick timeseries/map plot (maps per day of June 2023)

config = marEx.PlotConfig(plot_IDs=True)
fig, ax = june2023_events.ID_field.plotX.multi_plot(config, col="time", col_wrap=3)


# %%
from matplotlib import pyplot as plt

test = marEx_tracked.sel(time="2023-06-23")
plt.pcolormesh(test.ID_field, vmin=test.ID_field.max() - 12, vmax=test.ID_field.max())

# %%
merges = test.merge_ledger.where(test.merge_ledger > 0, drop=True)
merges

# plt.pcolormesh(merges)

# %%
