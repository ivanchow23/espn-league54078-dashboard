""" Owner draft position. """
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
draft_df_path = os.path.join("..", "docs", "data", "draft_df.csv")
draft_df = pd.read_csv(draft_df_path)

# %%
# Filter data for only the first round because this is essentially the draft order
draft_df = draft_df[draft_df['Round Number'] == 1]
draft_df['Draft Number'] = draft_df['Draft Number'].apply(_number_ordinal)

# %%
# Pie chart of number of times owner drafted in a particular position in the order
owners_list = sorted(draft_df['Owner Name'].unique())
specs = [[{'type': 'domain'} for i in range(0, len(owners_list))]]
fig = make_subplots(1, len(owners_list), specs=specs, subplot_titles=owners_list)

for i, owner in enumerate(owners_list):
    # Get counts and plot
    df = draft_df[draft_df['Owner Name'] == owner]
    value_counts = df['Draft Number'].value_counts().sort_index()
    fig.add_trace(go.Pie(labels=value_counts.index, values=value_counts, name=owner), 1, i + 1)

    # Add annotations to show information similar to a legend
    text = f"{owner}"
    for index in value_counts.index:
        text += f"<br>{index}: {value_counts[index]}/{value_counts.sum()} ({round((value_counts[index] / value_counts.sum()) * 100, 1)}%)"

    annotation_start_x = (1 - (0.125 * len(owners_list))) / 2
    annotation_location_x = annotation_start_x + (i * 0.125)
    fig.add_annotation(text=text, x=annotation_location_x, y=0.2, align='center', xanchor='left', yanchor='top', bordercolor='black',
                       borderwidth=0.25, borderpad=5, width=125, showarrow=False)

fig.update_layout(title="Owner Draft Positions", width=1400, height=500)
fig.show()
# %%
