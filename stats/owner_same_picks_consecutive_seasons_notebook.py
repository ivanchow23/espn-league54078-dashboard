""" Find owners who drafted the same player in consecutive seasons. """
# %%
# Imports
#!/usr/bin/env python
import os
import pandas as pd

# %%
# Helper functions
def _get_previous_season_string_int(curr_season_string_int):
    """ Returns the previous season string as an integer.
        Example: current season string int: 20192020
        Returns: 20182019 """
    # Simply parse the first 4 digits of the season string
    # Example: 20192020 will give 2019 here
    curr_season_int = int(str(curr_season_string_int)[:4])

    # Build previous season string by subtracting current by -1
    return int(f"{curr_season_int - 1}{curr_season_int}")

# %%
# Configurations
draft_df_path = os.path.join("..", "docs", "data", "draft_df.csv")
draft_df = pd.read_csv(draft_df_path)

# %%
# Get all seasons of interest
season_ints = draft_df['Season'].unique()

# %%
# Go through each season and find owners who drafted the same player in consecutive seasons
multi_season_df = pd.DataFrame()
for current_season in season_ints:
    previous_season = _get_previous_season_string_int(current_season)

    # Filter data for previous and current season
    current_season_df = draft_df[draft_df['Season'] == current_season]
    previous_season_df = draft_df[draft_df['Season'] == previous_season]

    if len(previous_season_df) == 0:
        continue

    # Get players drafted by same owner between consecutive seasons
    # Use an inner merge to keep only the players common to current season from previous season
    multi_df = pd.DataFrame()
    for owner, curr_df in current_season_df.groupby('Owner Name'):
        # Check if owner had drafts/data from previous season
        prev_df = previous_season_df[previous_season_df['Owner Name'] == owner]
        if prev_df.empty:
            continue

        merge_df = curr_df.merge(prev_df, how='inner', on=['Player', 'Position'])[['Player']]
        new_df = pd.DataFrame(columns=pd.MultiIndex.from_product([[owner], merge_df.columns]))
        new_df[owner] = merge_df
        multi_df = pd.concat([multi_df, new_df], axis=1)

    multi_df['Season'] = current_season
    multi_df = multi_df.set_index(['Season', multi_df.index])
    multi_season_df = pd.concat([multi_season_df, multi_df])

multi_season_df.to_csv("owner_same_picks_consecutive_seasons.csv")
