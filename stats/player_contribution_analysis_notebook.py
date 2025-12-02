""" Stats on player contribution for an owner per season compared to the league. """
# %%
# Imports
#!/usr/bin/env python
import os
import pandas as pd

# %%
# Helper functions
def _get_season_max_position_slots(season_df, pos_key):
    """ Function to determine the limits of each position. Meant to be very
        simple and crude. Simply looks at the first scoring period and takes
        the max value between each owner. Essentially assumes at least one
        owner filled out all allocated position slots in the first day. """
    first_scoring_period_df = season_df[season_df['scoringPeriodId'] == 1]
    first_scoring_period_df = first_scoring_period_df[first_scoring_period_df['position'] == pos_key]
    return max(first_scoring_period_df.groupby('owner').size())

# %%
# Configurations
daily_rosters_df_path = os.path.join("..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")
cols_of_interest = ['GP', 'appliedTotal', 'G', 'A', 'PPP', 'SHP', 'GWG', 'HAT', 'W', 'SO']
daily_rosters_df = pd.read_csv(daily_rosters_df_path)

# %%
# Omit slots where player is on bench or IR, which appear to be slots 7 and 8
daily_rosters_df = daily_rosters_df[(daily_rosters_df['lineupSlotId'] != 7) & (daily_rosters_df['lineupSlotId'] != 8)]

# %%
# Remap lineup slot to position names
daily_rosters_non_ir_bench_df = daily_rosters_df.copy(deep=True)
daily_rosters_non_ir_bench_df['lineupSlotId'] = daily_rosters_non_ir_bench_df['lineupSlotId'].replace(3, "Forwards")
daily_rosters_non_ir_bench_df['lineupSlotId'] = daily_rosters_non_ir_bench_df['lineupSlotId'].replace(4, "Defencemen")
daily_rosters_non_ir_bench_df['lineupSlotId'] = daily_rosters_non_ir_bench_df['lineupSlotId'].replace(5, "Goalies")
daily_rosters_non_ir_bench_df = daily_rosters_non_ir_bench_df.rename(columns={'lineupSlotId': 'position'})

# %%
# Create a new combined dataframe with player contribution stats for each position for all seasons
combined_df = pd.DataFrame()
for season, season_df in daily_rosters_non_ir_bench_df.groupby('season'):
    # Get number of owners in the season
    num_owners = len(season_df['owner'].unique())

    # Sum contributions of each player for each position for each owner
    total_df = season_df.groupby(['fullName', 'position', 'owner'])[cols_of_interest].sum().reset_index()
    total_df['appliedTotal/GP'] = round(total_df['appliedTotal'] / total_df['GP'], 2)

    # Analyze contributions of each player in each position
    print(season)
    for pos, pos_df in total_df.groupby('position'):
        # Normalize by max slots for the season
        num_slots = _get_season_max_position_slots(season_df, pos)
        avg_pts_per_slot = pos_df['appliedTotal'].sum() / num_slots / num_owners
        print(f"Average points per slot for {pos}: {round(avg_pts_per_slot, 2)}")

        # This is how many slots does the player actually take up based on their
        # accumulated total compared to league average points contribution per slot
        # Examples:  1 = player contributes exactly one slot worth
        #          > 1 = player contributes more than a slot worth of points
        #          < 1 = player contributes less than a slot worth of points
        pos_df['slot_value'] = round(pos_df['appliedTotal'] / avg_pts_per_slot, 2)

        pos_df['season'] = season
        combined_df = pd.concat([combined_df, pos_df], ignore_index=True)
    print()
combined_df.to_csv("player_contribution_analysis.csv", index=False)
# %%
