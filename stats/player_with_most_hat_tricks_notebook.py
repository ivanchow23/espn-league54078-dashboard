""" Find the player that gets the most hat tricks since
    the league started counting them. """
# %%
# Imports
#!/usr/bin/env python
import os
import pandas as pd

# %%
# Configurations
daily_rosters_df_path = os.path.join("..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")
daily_rosters_df = pd.read_csv(daily_rosters_df_path)

# %%
# Filter for stat column where hat trick values are populated
hat_tricks_df = daily_rosters_df.dropna(subset=['HAT'])

# %%
# Count number of hat tricks for each player
hat_tricks_series = hat_tricks_df['fullName'].value_counts()
hat_tricks_series.to_csv("num_hat_tricks.csv")
hat_tricks_series
# %%
