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
