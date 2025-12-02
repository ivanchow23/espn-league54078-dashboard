""" Games lost due to player being out on roster (not placed in IR slot).
    Note: Goalies not starting a game also appears as "man games lost" """
# %%
# Imports
#!/usr/bin/env python
from man_games_lost import ManGamesLost
import os

# %%
# Configurations
daily_rosters_df_path = os.path.join("..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")
mgl = ManGamesLost(daily_rosters_df_path)
seasons = mgl.get_seasons()

# %%
# Show data for each season
for season in seasons:
    fig = mgl.get_table_fig(season)
    fig.show()
