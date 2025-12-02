""" Player contribution for an owner per season compared to the league
    compared to the position they were drafted. """
# %%
# Imports
#!/usr/bin/env python
import os
import pandas as pd
import plotly.graph_objects as go

# %%
# Configurations
daily_rosters_df_path = os.path.join("..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")
draft_df_path = os.path.join("..", "docs", "data", "draft_df.csv")
daily_rosters_col_of_interest = ['GP', 'appliedTotal', 'G', 'A', 'PPP', 'SHP', 'GWG', 'HAT', 'W', 'SO']

daily_rosters_df = pd.read_csv(daily_rosters_df_path)
draft_df = pd.read_csv(draft_df_path)

# %%
# Omit slots where player is on bench or IR, which appear to be slots 7 and 8
daily_rosters_df = daily_rosters_df[(daily_rosters_df['lineupSlotId'] != 7) & (daily_rosters_df['lineupSlotId'] != 8)]

# %%
# Plot bar chart of points vs. draft number for each season
for (draft_season, draft_season_df), (roster_season, roster_season_df) in zip(draft_df.groupby('Season'), daily_rosters_df.groupby('season')):
    # Sum total points for each player
    players_sum_df = roster_season_df.groupby(['fullName', 'lineupSlotId'])[daily_rosters_col_of_interest].sum().reset_index()

    # Merge with draft information
    combined_df = draft_season_df[['Draft Number', 'Round Number', 'Player', 'Owner Name']].merge(players_sum_df, left_on='Player', right_on='fullName', how='inner')

    # Plot bar chart
    fig = go.Figure()
    for owner, owner_df in combined_df.groupby('Owner Name'):
        fig.add_trace(go.Bar(x=owner_df['Draft Number'], y=owner_df['appliedTotal'], hovertext=owner_df['Player'], name=owner))
    fig.update_layout(title=f"Player Contributed Points for Owner vs. Draft Number ({draft_season})",
                      xaxis_title="Draft Number", yaxis_title="Points")
    fig.show()
# %%
