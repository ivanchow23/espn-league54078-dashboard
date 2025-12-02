""" Analysis of draft age. """
# %%
# Imports
#!/usr/bin/env python
import os
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# %%
# Configurations
draft_df_path = os.path.join("..", "docs", "data", "draft_df.csv")
draft_df = pd.read_csv(draft_df_path)

# %%
# Each owner's overall distribution of drafted age
owners_list = sorted(draft_df['Owner Name'].unique())
fig = make_subplots(rows=1, cols=len(draft_df['Owner Name'].unique()), shared_xaxes='all', shared_yaxes='all', subplot_titles=owners_list)
for i, owner in enumerate(owners_list):
    owner_df = draft_df[draft_df['Owner Name'] == owner]

    # Stats
    mean = round(owner_df['Player Age'].mean(), 1)
    min = float(owner_df['Player Age'].min())
    max = float(owner_df['Player Age'].max())

    fig.add_trace(go.Histogram(x=owner_df['Player Age'], histnorm='percent', name=f"{owner} (min={min} avg={mean} max={max})"), 1, i + 1)
fig.update_layout(title="Distribution of Owner's Draft Picks (Overall)", xaxis_title="Age", yaxis_title="% of Picks", width=1400, height=500)
fig.show()
# %%
# Each owner's distrubution of drafted age per season
for season, season_df in draft_df.groupby('Season'):
    owners_list = sorted(season_df['Owner Name'].unique())
    fig = make_subplots(rows=1, cols=len(draft_df['Owner Name'].unique()), shared_xaxes='all', shared_yaxes='all', subplot_titles=owners_list)
    for i, owner in enumerate(owners_list):
        owner_df = season_df[season_df['Owner Name'] == owner]

        # Stats
        mean = round(owner_df['Player Age'].mean(), 1)
        min = float(owner_df['Player Age'].min())
        max = float(owner_df['Player Age'].max())

        fig.add_trace(go.Histogram(x=owner_df['Player Age'], histnorm='percent', name=f"{owner} (min={min} avg={mean} max={max})"), 1, i + 1)
    fig.update_layout(title=f"Distribution of Owner's Draft Picks ({season})", xaxis_title="Age", yaxis_title="% of Picks", width=1400, height=500)
    fig.show()
