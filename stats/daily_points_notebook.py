# %%
# Imports
#!/usr/bin/env python
from daily_points import DailyPoints
import os

# %%
# Configurations
daily_rosters_df_path = os.path.join("..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")
dp = DailyPoints(daily_rosters_df_path)
seasons = dp.get_seasons()

# %%
# Plot raw cumulative total
for season in seasons:
    fig = dp.get_cumulative_points_plot(key="appliedTotal", season=season)
    fig.show()

# %%
# Plot cumulative total normalized by average
for season in seasons:
    fig = dp.get_cumulative_points_norm_by_avg_plot(key="appliedTotal", season=season)
    fig.show()

# %%
# Plot cumulative total normalized by first place
for season in seasons:
    fig = dp.get_cumulative_points_norm_by_first_plot(key="appliedTotal", season=season)
    fig.show()