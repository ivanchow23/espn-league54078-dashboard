""" Analysis and breakdown of points by positions. """
# %%
# Imports
#!/usr/bin/env python
import os
from points_by_position import PointsByPosition

# %%
# Configurations
daily_rosters_df_path = os.path.join("..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")
pbp = PointsByPosition(daily_rosters_df_path)
seasons = pbp.get_seasons()

# %%
# Plot
for season in seasons:
    fig = pbp.get_stats_table(season)
    fig.show()