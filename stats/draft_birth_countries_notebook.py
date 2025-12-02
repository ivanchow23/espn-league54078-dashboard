""" Analysis of draft birth countries. """
# %%
# Imports
#!/usr/bin/env python
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# %%
# Configurations
draft_df_path = os.path.join("..", "docs", "data", "draft_df.csv")
draft_df = pd.read_csv(draft_df_path)

wedge_colour_map={"CAN": '#cd5c5c',
                  "USA": '#4169e1',
                  "RUS": '#fffafa',
                  "SWE": '#ffd700',
                  "FIN": '#000080',
                  "CZE": '#add8e6',
                  "CHE": '#b22222',
                  "DEU": '#696969'}
# %%
# Each owner's overall distribution of drafted birth countries
owners_list = sorted(draft_df['Owner Name'].unique())
specs = [[{'type': 'domain'} for i in range(0, len(owners_list))]]
fig = make_subplots(1, len(owners_list), specs=specs, subplot_titles=owners_list)

for i, owner in enumerate(owners_list):
    df = draft_df[draft_df['Owner Name'] == owner]
    value_counts = df['Player Birth Country'].value_counts().sort_index()
    wedge_colours = [wedge_colour_map[index] if index in wedge_colour_map else "darkgray" for index in value_counts.index]
    fig.add_trace(go.Pie(labels=value_counts.index, values=value_counts, name=owner, marker_colors=wedge_colours), 1, i + 1)

fig.update_layout(title="Distribution of Owner's Draft Birth Countries (Overall)", width=1400, height=600)
fig.show()
# %%
# Each owner's distrubution of drafted age per season
for season, season_df in draft_df.groupby('Season'):
    owners_list = sorted(season_df['Owner Name'].unique())
    specs = [[{'type': 'domain'} for i in range(0, len(owners_list))]]
    fig = make_subplots(1, len(owners_list), specs=specs, subplot_titles=owners_list)

    for i, owner in enumerate(owners_list):
        df = season_df[season_df['Owner Name'] == owner]
        value_counts = df['Player Birth Country'].value_counts().sort_index()
        wedge_colours = [wedge_colour_map[index] if index in wedge_colour_map else "darkgray" for index in value_counts.index]
        fig.add_trace(go.Pie(labels=value_counts.index, values=value_counts, name=owner, marker_colors=wedge_colours), 1, i + 1)

    fig.update_layout(title=f"Distribution of Owner's Draft Birth Countries ({season})", width=1400, height=500)
    fig.show()