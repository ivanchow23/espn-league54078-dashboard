""" Analysis of points per season. """
# %%
# Imports
#!/usr/bin/env python
import os
import pandas as pd
import plotly.graph_objects as go

# %%
# Configurations
standings_points_df_path = os.path.join("..", "docs", "data", "standings_points_df.csv")
standings_points_df = pd.read_csv(standings_points_df_path)

# %%
# Normalize points per season
norm_df = pd.DataFrame()
for season, season_df in standings_points_df.groupby('Season'):
    season_norm_df = season_df

    # Normalize by average and highest points
    season_norm_df['Normalized By Average'] = round(season_norm_df['TOT'] / season_norm_df['TOT'].mean(), 3)
    season_norm_df['Normalized By Max'] = round(season_norm_df['TOT'] / season_norm_df['TOT'].max(), 3)

    # Combine normalized dataframe
    norm_df = pd.concat([norm_df, season_norm_df], ignore_index=True)

# %%
# Plot normalized final points by average per season of each owner
fig = go.Figure()
for owner, owner_df in norm_df.groupby('Owner'):
    # Stats
    min = round(owner_df['Normalized By Average'].min(), 2)
    avg = round(owner_df['Normalized By Average'].mean(), 2)
    max = round(owner_df['Normalized By Average'].max(), 2)

    # Plot
    fig.add_trace(go.Scatter(x=owner_df['Season'].apply(str), y=owner_df['Normalized By Average'],
                  name=f"{owner} (Avg={avg} Max={max} Min={min})"))

fig.update_layout(title="Points (Normalized by Average) vs. Season", xaxis_title="Season", yaxis_title="Points (Normalized by Average)",
                  width=1200, height=400)
fig.show()

# %%
# Plot normalized final points by first per season of each owner
fig = go.Figure()
for owner, owner_df in norm_df.groupby('Owner'):
    # Stats
    min = round(owner_df['Normalized By Max'].min(), 2)
    avg = round(owner_df['Normalized By Max'].mean(), 2)
    max = round(owner_df['Normalized By Max'].max(), 2)

    # Plot
    fig.add_trace(go.Scatter(x=owner_df['Season'].apply(str), y=owner_df['Normalized By Max'],
                  name=f"{owner} (Avg={avg} Max={max} Min={min})"))

fig.update_layout(title="Points (Normalized by First) vs. Season", xaxis_title="Season", yaxis_title="Points (Normalized by First)",
                  width=1200, height=400)
fig.show()
# %%
