# %%
import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from vosse.analysis.params import FPaths

# %%

blobs: xr.DataArray = xr.open_dataset(FPaths.ocetrac_blobs).blobs

# %%
# ---------------------------------------------------------------------------
# 1. EVENT FREQUENCY MAP
#    Fraction of time steps where any tracked MHW is present at each grid cell
# ---------------------------------------------------------------------------

event_frequency = (blobs > 0).mean("time").compute()

fig, ax = plt.subplots(
    figsize=(10, 6),
    subplot_kw={"projection": ccrs.PlateCarree()},
)
ax.add_feature(cfeature.LAND, color="lightgrey", zorder=3)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5, zorder=4)
ax.gridlines(draw_labels=True, linewidth=0.3, linestyle="--", alpha=0.6)

im = ax.pcolormesh(
    blobs.longitude,
    blobs.latitude,
    event_frequency,
    cmap="hot_r",
    transform=ccrs.PlateCarree(),
    vmin=0,
)
plt.colorbar(im, ax=ax, label="MHW presence frequency", shrink=0.7)
ax.set_title("Ocetrac – MHW event frequency (fraction of time steps)")
plt.tight_layout()
plt.savefig(os.path.join(FPaths.plot_dir, "ocetrac_event_frequency.png"), dpi=150)
plt.show()

# %%
# ---------------------------------------------------------------------------
# 2. SEASONAL EVENT FREQUENCY (4-panel)
# ---------------------------------------------------------------------------

seasonal_freq = (blobs > 0).groupby("time.season").mean("time").compute()
seasons = ["DJF", "MAM", "JJA", "SON"]

fig, axes = plt.subplots(
    2,
    2,
    figsize=(14, 8),
    subplot_kw={"projection": ccrs.PlateCarree()},
)
vmax = float(seasonal_freq.max())

for ax, season in zip(axes.flat, seasons):
    if season not in seasonal_freq.season.values:
        ax.set_visible(False)
        continue
    ax.add_feature(cfeature.LAND, color="lightgrey", zorder=3)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, zorder=4)
    ax.gridlines(draw_labels=False, linewidth=0.3, linestyle="--", alpha=0.6)
    im = ax.pcolormesh(
        blobs.longitude,
        blobs.latitude,
        seasonal_freq.sel(season=season),
        cmap="hot_r",
        vmin=0,
        vmax=vmax,
        transform=ccrs.PlateCarree(),
    )
    ax.set_title(season)

fig.colorbar(im, ax=axes, label="MHW presence frequency", shrink=0.6, pad=0.02)
fig.suptitle("Ocetrac – Seasonal MHW frequency", fontsize=13)
plt.savefig(os.path.join(FPaths.plot_dir, "ocetrac_seasonal_frequency.png"), dpi=150)
plt.show()

# %%
# ---------------------------------------------------------------------------
# 3. NUMBER OF UNIQUE EVENTS THROUGH TIME  (monthly count)
# ---------------------------------------------------------------------------

# Count distinct blob IDs present at each time step, then resample monthly
n_events_daily = (
    blobs.where(blobs > 0)
    .groupby("time")
    .apply(lambda x: xr.DataArray(int(np.nanmax(x.values)) if np.any(~np.isnan(x.values)) else 0))
)

# Simpler: count unique non-nan labels per time step via a loop (manageable size)
n_events = []
times = blobs.time.values
for t in range(len(times)):
    snap = blobs.isel(time=t).values
    n_events.append(len(np.unique(snap[~np.isnan(snap)])))

n_events_da = xr.DataArray(n_events, coords={"time": times}, dims=["time"])
n_events_monthly = n_events_da.resample(time="ME").mean()

fig, ax = plt.subplots(figsize=(14, 4))
n_events_monthly.plot(ax=ax, color="steelblue", lw=1.5)
ax.set_ylabel("Mean number of active MHW objects")
ax.set_xlabel("Time")
ax.set_title("Ocetrac – Monthly mean count of active tracked MHW objects")
ax.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(FPaths.plot_dir, "ocetrac_event_count_timeseries.png"), dpi=150)
plt.show()

# %%
# ---------------------------------------------------------------------------
# 4. LATITUDE–TIME HOVMÖLLER  (MHW presence averaged over longitude)
# ---------------------------------------------------------------------------

hovmoller = (blobs > 0).mean("longitude").resample(time="ME").mean().compute()

fig, ax = plt.subplots(figsize=(14, 6))
im = hovmoller.plot(
    ax=ax,
    cmap="hot_r",
    x="time",
    y="latitude",
    cbar_kwargs={"label": "MHW presence frequency"},
    add_colorbar=True,
)
ax.set_title("Ocetrac – Hovmöller: MHW presence frequency (lon-averaged, monthly)")
ax.set_xlabel("Time")
ax.set_ylabel("Latitude")
ax.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig(os.path.join(FPaths.plot_dir, "ocetrac_hovmoller.png"), dpi=150)
plt.show()

# %%
# ---------------------------------------------------------------------------
# 5. SNAPSHOT OF THE LARGEST EVENT  (map of blob IDs at its peak time step)
# ---------------------------------------------------------------------------

# Find the time step with the most grid cells covered by any MHW
coverage = (blobs > 0).sum(dim=["latitude", "longitude"]).compute()
peak_t = int(coverage.argmax("time").values)
peak_time = blobs.time.values[peak_t]

snap = blobs.isel(time=peak_t).compute()

fig, ax = plt.subplots(
    figsize=(10, 6),
    subplot_kw={"projection": ccrs.PlateCarree()},
)
ax.add_feature(cfeature.LAND, color="lightgrey", zorder=3)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5, zorder=4)
ax.gridlines(draw_labels=True, linewidth=0.3, linestyle="--", alpha=0.6)

im = ax.pcolormesh(
    blobs.longitude,
    blobs.latitude,
    snap,
    cmap="tab20",
    transform=ccrs.PlateCarree(),
)
plt.colorbar(im, ax=ax, label="Blob ID", shrink=0.7)
ax.set_title(f"Ocetrac – Tracked MHW objects on peak coverage day\n{str(peak_time)[:10]}")
plt.tight_layout()
plt.savefig(os.path.join(FPaths.plot_dir, "ocetrac_peak_snapshot.png"), dpi=150)
plt.show()

# %%
