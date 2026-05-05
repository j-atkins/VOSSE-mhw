# %%

import os

from cartopy import crs as ccrs
import marEx
from matplotlib import pyplot as plt
import xarray as xr

from vosse.analysis.params import FPaths

# %%

marEx_tracked = xr.open_dataset(FPaths.marEx_tracked)
marEx_tracked = marEx_tracked.rename({"latitude": "lat", "longitude": "lon"})

# %%

# Plot global extreme event frequency
event_frequency = (marEx_tracked.ID_field > 0).mean("time")

# Configure plot appearance
config = marEx.PlotConfig(var_units="MHW Frequency", cmap="hot_r", cperc=[0, 96], grid_labels=True)

# Create single plot
fig, ax, im = event_frequency.plotX.single_plot(config)

# %%

# Multi-panel visualisation: seasonal extreme event frequency
seasonal_frequency = (marEx_tracked.ID_field > 0).groupby("time.season").mean(dim="time")

# Configure plot appearance
config = marEx.PlotConfig(var_units="MHW Frequency", cmap="hot_r", cperc=[0, 96], grid_labels=True)

# Create multi-panel plot
fig, ax = seasonal_frequency.plotX.multi_plot(config, col="season", col_wrap=2)


# %%

os.makedirs(FPaths.plot_dir, exist_ok=True)

# # Create animation of tracked events
# ID_field_subset = marEx_tracked.ID_field.sel(time=slice("2023-01-01", "2023-12-31"))
# config = marEx.PlotConfig(plot_IDs=True)
# ID_field_subset.plotX.animate(config, plot_dir=FPaths.plot_dir, file_name="marine_heatwaves")

# # Plot consecutive time periods
# ID_field_subset = marEx_tracked.ID_field.sel(time=slice("2021-01-01", "2021-01-06"))
# config = marEx.PlotConfig(plot_IDs=True)
# fig, ax = ID_field_subset.plotX.multi_plot(config, col="time", col_wrap=3)


# %%

events_duration = marEx_tracked.time_end - marEx_tracked.time_start
longest_events = events_duration.sortby(events_duration, ascending=False).ID

for ID in longest_events[:10].values:
    print(
        f"ID: {ID:<6}   Start Day: {marEx_tracked.time_start.sel(ID=ID).dt.strftime('%Y-%m-%d').values}  -->  Duration: {events_duration.sel(ID=ID).dt.days.values:<4} days"
    )

long_events = marEx_tracked.ID_field == (longest_events[:9]).chunk({"ID": 1})
long_events_local_duration = (long_events > 0).sum("time")

config = marEx.PlotConfig(
    var_units="Duration (days)",
    cmap="hot_r",
    cperc=[0, 100],
    projection=ccrs.PlateCarree(),
)
fig, ax = long_events_local_duration.plotX.multi_plot(config, col="ID", col_wrap=3)

# %%

area = marEx_tracked.area.chunk({"ID": 1000, "time": 100})
area_mean = area.mean("ID").resample(time="ME").mean().compute()

area_quantiles = (area.quantile([0.1, 0.9], dim="ID").resample(time="ME").mean()).compute()

area_10 = area_quantiles.sel(quantile=0.1)
area_90 = area_quantiles.sel(quantile=0.9)

plt.figure(figsize=(15, 6))
area_mean.plot(label="Mean Area", color="k", lw=2)
plt.fill_between(area_mean.time.values, area_10, area_90, alpha=0.5)
# plt.ylim([0, 1e7])
# plt.ylabel(r"Event Area [km$^2$]")

# %%


spatial_presence = (marEx_tracked.ID_field > 0).mean(dim="lon").resample(time="ME").mean()

fig, ax = plt.subplots(figsize=(15, 6))
im = spatial_presence.plot(
    ax=ax,
    cmap="hot",
    x="time",
    cbar_kwargs={"label": "MHW Presence Frequency", "extend": "both"},
)

ax.set_xlabel("Time")
ax.set_ylabel("Latitude")
ax.grid(True, linestyle="--", alpha=0.6)

# %%

events_intensity = marEx_tracked.time_end - marEx_tracked.time_start
longest_events = events_duration.sortby(events_duration, ascending=False).ID

for ID in longest_events[:10].values:
    print(
        f"ID: {ID:<6}   Start Day: {marEx_tracked.time_start.sel(ID=ID).dt.strftime('%Y-%m-%d').values}  -->  Duration: {events_duration.sel(ID=ID).dt.days.values:<4} days"
    )

long_events = marEx_tracked.ID_field == (longest_events[:9]).chunk({"ID": 1})
long_events_local_duration = (long_events > 0).sum("time")

config = marEx.PlotConfig(
    var_units="Duration (days)",
    cmap="hot_r",
    cperc=[0, 100],
    projection=ccrs.PlateCarree(),
)
fig, ax = long_events_local_duration.plotX.multi_plot(config, col="ID", col_wrap=3)
