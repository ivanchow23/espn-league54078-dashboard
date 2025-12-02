""" Notebook to determine who drafts the biggest "goons" on their team
(i.e. who drafts players with the most PIM and HITS). """
# %%
# Imports
import os
import pandas as pd
import plotly.express as px

# %%
# Configurations
draft_df_path = os.path.join("..", "docs", "data", "draft_df.csv")
draft_df = pd.read_csv(draft_df_path)

# Group by 'Season' and 'Owner Name' and calculate the sum of 'PIM'
grouped_data_PIM = draft_df.groupby(['Season', 'Owner Name'])['PIM'].sum().reset_index()

# Group by 'Season' and 'Owner Name' and calculate the sum of 'HITS'
grouped_data_HITS = draft_df.groupby(['Season', 'Owner Name'])['HITS'].sum().reset_index()

# Select unique owner names for colour map generation
unique_owners = draft_df['Owner Name'].unique()

# Generate colour map
colour_cycle = px.colors.qualitative.Dark24
colour_map = dict(zip(unique_owners, colour_cycle))

# %%
# Across all seasons, find the owner who had the highest sum of PIMs

# Find the Owner Name with the highest sum of PIM for each season
max_pim_per_season = grouped_data_PIM.loc[grouped_data_PIM.groupby('Season')['PIM'].idxmax()]

fig = px.bar(max_pim_per_season, x='Season', y='PIM', color='Owner Name',
             title='Owner with Highest Sum of Drafted Players PIM for Each Season',
             labels={'PIM': 'Sum of PIM'},
             color_discrete_map=colour_map)

# Update layout to prevent x-axis label abbreviation
fig.update_layout(xaxis_title='Season', yaxis_title='Sum of PIM',
                  xaxis=dict(tickmode='array', tickvals=max_pim_per_season['Season'].tolist(),
                             ticktext=[str(season) for season in max_pim_per_season['Season']]))
fig.show()

# %%
# Across all seasons, find the owner who had the least sum of PIMs

# Find the Owner Name with the smallest sum of PIM for each season
min_pim_per_season = grouped_data_PIM.loc[grouped_data_PIM.groupby('Season')['PIM'].idxmin()]

# Create a bar plot to show which "Owner Name" has the smallest sum of "PIM" for each "Season"
fig = px.bar(min_pim_per_season, x='Season', y='PIM', color='Owner Name',
             title='Owner with Lowest Sum of Drafted Players PIM for Each Season',
             labels={'PIM': 'Sum of PIM'},
             color_discrete_map=colour_map,
             category_orders={"Season": draft_df['Season'].unique()})

fig.update_layout(xaxis_title='Season', yaxis_title='Sum of PIM',
                  xaxis={'tickmode': 'array', 'tickvals': min_pim_per_season['Season'].tolist(),
                         'ticktext': [str(season) for season in min_pim_per_season['Season']]})

fig.show()

# %%
# Across all seasons, find the owner who had the highest sum of HITS

# Find the Owner Name with the highest sum of PIM for each season
max_hits_per_season = grouped_data_HITS.loc[grouped_data_HITS.groupby('Season')['HITS'].idxmax()]

max_hits_per_season = grouped_data_HITS.loc[grouped_data_HITS.groupby('Season')['HITS'].idxmax()]

# Create a bar plot to show which "Owner Name" has the highest sum of "HITS" for each "Season"
fig = px.bar(max_hits_per_season, x='Season', y='HITS', color='Owner Name',
             title='Owner with Highest Sum of Drafted Players HITS for Each Season',
             labels={'HITS': 'Sum of HITS'},
             color_discrete_map=colour_map)

fig.update_layout(xaxis_title='Season', yaxis_title='Sum of HITS',
                  xaxis=dict(tickmode='array', tickvals=max_hits_per_season['Season'].tolist(),
                             ticktext=[str(season) for season in max_hits_per_season['Season']]))

fig.show()

# %%
# Across all seasons, find the owner who had the least sum of HITS

# Find the Owner Name with the smallest sum of HITS for each season
min_hits_per_season = grouped_data_HITS.loc[grouped_data_HITS.groupby('Season')['HITS'].idxmin()]

# Create a bar plot to show which "Owner Name" has the smallest sum of "HITS" for each "Season"
fig = px.bar(min_hits_per_season, x='Season', y='HITS', color='Owner Name',
             title='Owner with Lowest Sum of Drafted Players HITS for Each Season',
             labels={'HITS': 'Sum of HITS'},
             color_discrete_map=colour_map,
             category_orders={"Season": draft_df['Season'].unique()})

fig.update_layout(xaxis_title='Season', yaxis_title='Sum of HITS',
                  xaxis={'tickmode': 'array', 'tickvals': min_hits_per_season['Season'].tolist(),
                         'ticktext': [str(season) for season in min_hits_per_season['Season']]})
fig.show()

# %%
# Generate bar chart to show which "Owner Name" has the highest sum of "PIM" per "Season"
for season, season_data_PIM_df in grouped_data_PIM.groupby('Season'):
    season_data_PIM_df = season_data_PIM_df.sort_values(by='PIM', ascending=False)

    fig = px.bar(season_data_PIM_df, x='Owner Name', y='PIM', color='Owner Name',
                 title=f'Sum of Drafted Players PIM by Owner for {season}', labels={'PIM': 'Sum of PIM'},
                 color_discrete_map=colour_map)

    fig.update_layout(xaxis_title='Owner Name', yaxis_title='Sum of PIM', showlegend=False)
    fig.show()

# %%
# Generate bar chart to show which "Owner Name" has the highest sum of "HITS" per "Season"

# Generate bar graph for each unique 'Season' with sorting by HITS
for season, season_data_HITS_df in grouped_data_HITS.groupby('Season'):
    season_data_HITS_df = season_data_HITS_df.sort_values(by='HITS', ascending=False)

    fig = px.bar(season_data_HITS_df, x='Owner Name', y='HITS', color='Owner Name',
                 title=f'Sum of Drafted Players HITS by Owner for {season}', labels={'HITS': 'Sum of HITS'},
                 color_discrete_map=colour_map)

    fig.update_layout(xaxis_title='Owner Name', yaxis_title='Sum of HITS', showlegend=False)
    fig.show()

# %%
# Generate bar chart to show the top 10 "Players" per "Season" that have the highest "PIM" and their corresponding "Owner Name"

# Group by 'Season', 'Owner Name', and 'Player', calculate the sum of 'PIM'
grouped_data_PIM_player = draft_df.groupby(['Season', 'Owner Name', 'Player'])['PIM'].sum().reset_index()

# Find the top 10 players with the most PIM for each season
top_players_per_season = []

for season, season_data_PIM_df in grouped_data_PIM_player.groupby('Season'):

    # Sort by 'PIM' in descending order and select the top 10
    top_players_PIM = season_data_PIM_df.sort_values(by='PIM', ascending=False).head(10)
    top_players_per_season.append(top_players_PIM)

# Create a bar plot for each season with assigned legend colors
for idx, season_top_players in enumerate(top_players_per_season):
    fig = px.bar(season_top_players, x='Player', y='PIM', color='Owner Name',
                 title=f'Top 10 Drafted Players with Most PIM - {draft_df["Season"].unique()[idx]}',
                 labels={'PIM': 'Sum of PIM'},
                 color_discrete_map=colour_map)

    fig.update_layout(xaxis_title='Player', yaxis_title='Sum of PIM', xaxis={'categoryorder':'total descending'})
    fig.show()

# %%
# Generate bar chart to show the top 10 "Player"s per "Season" that have the highest "HITS" and their corresponding "Owner Name"

# Group by 'Season', 'Owner Name', and 'Player', calculate the sum of 'HITS'
grouped_data_HITS_player = draft_df.groupby(['Season', 'Owner Name', 'Player'])['HITS'].sum().reset_index()

# Find the top 10 players with the most PIM for each season
top_players_per_season = []
for season, season_data_HITS_df in grouped_data_HITS_player.groupby('Season'):

    # Sort by 'HITS' in descending order and select the top 10
    top_players_HITS = season_data_HITS_df.sort_values(by='HITS', ascending=False).head(10)
    top_players_per_season.append(top_players_HITS)

# Create a bar plot for each season with assigned legend colors
for idx, season_top_players in enumerate(top_players_per_season):
    fig = px.bar(season_top_players, x='Player', y='HITS', color='Owner Name',
                 title=f'Top 10 Drafted Players with Most HITS - {draft_df["Season"].unique()[idx]}',
                 labels={'PIM': 'Sum of HITS'},
                 color_discrete_map=colour_map)

    fig.update_layout(xaxis_title='Player', yaxis_title='Sum of HITS', xaxis={'categoryorder':'total descending'})
    fig.show()
