""" Analysis of each owner's rankings. """
# %%
# Imports
#!/usr/bin/env python
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# %%
# Helper functions
def _number_ordinal(val):
    """ Simple function to convert an integer to a "numerical ordinal"
        string. Example: 1, 2, 3, 4 -> 1st, 2nd, 3rd, 4th. """
    if val == 1:
        return "1st"
    elif val == 2:
        return "2nd"
    elif val == 3:
        return "3rd"
    else:
        return f"{val}th"

# %%
# Configurations
standings_points_df_path = os.path.join("..", "docs", "data", "standings_points_df.csv")
standings_points_df = pd.read_csv(standings_points_df_path)

# %%
# Convert rankings to ordinal
standings_points_df['RK'] = standings_points_df['RK'].apply(_number_ordinal)

# %%
# Pie chart of each owner's rankings
wedge_colour_map = {"1st": '#ffd700',
                    "2nd": '#b0c4de',
                    "3rd": '#d2b48c'}

owners_list = sorted(standings_points_df['Owner'].unique())
specs = [[{'type': 'domain'} for i in range(0, len(owners_list))]]
fig = make_subplots(1, len(owners_list), specs=specs, subplot_titles=owners_list)

for i, owner in enumerate(owners_list):
    # Get counts and plot
    df = standings_points_df[standings_points_df['Owner'] == owner]
    value_counts = df['RK'].value_counts().sort_index()
    wedge_colours = [wedge_colour_map[index] if index in wedge_colour_map else "darkgray" for index in value_counts.index]
    fig.add_trace(go.Pie(labels=value_counts.index, values=value_counts, name=owner, marker_colors=wedge_colours), 1, i + 1)

    # Add annotations to show information similar to a legend
    text = f"{owner}"
    for index in value_counts.index:
        text += f"<br>{index}: {value_counts[index]}/{value_counts.sum()} ({round((value_counts[index] / value_counts.sum()) * 100, 1)}%)"

    annotation_start_x = (1 - (0.125 * len(owners_list))) / 2
    annotation_location_x = annotation_start_x + (i * 0.125)
    fig.add_annotation(text=text, x=annotation_location_x, y=0.2, align='center', xanchor='left', yanchor='top', bordercolor='black',
                       borderwidth=0.25, borderpad=5, width=125, showarrow=False)

fig.update_layout(title="Rankings", width=1400, height=500)
fig.show()