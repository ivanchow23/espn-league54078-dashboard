""" Analyzes if any players had multiple owners (due to trade, FA, etc.)
    every season and calculate the points scored for each owner. """
# %%
# Imports
#!/usr/bin/env python
import os
from player_with_different_owners import PlayerWithDifferentOwners

# %%
# Configurations
daily_rosters_df_path = os.path.join("..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")
all_players_df_path = os.path.join("..", "docs", "data", "espn_fantasy_api_all_players_info_df.csv")
pwdo = PlayerWithDifferentOwners(daily_rosters_df_path, all_players_df_path)
seasons = pwdo.get_seasons()

# %%
# Show data for each season
for season in seasons:
    fig = pwdo.get_table_fig(season)
    fig.show()