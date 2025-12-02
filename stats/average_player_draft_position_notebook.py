""" Get each player's average draft position. """
# %%
# Imports
#!/usr/bin/env python
import os
import pandas as pd
# %%
# Configurations
draft_df_path = os.path.join("..", "docs", "data", "draft_df.csv")
draft_df = pd.read_csv(draft_df_path)

# %%
# Get each player's average draft position
grouped_df = draft_df.groupby(['Player'])['Draft Number'].agg(['mean', 'min', 'max', 'count']).round(0)
grouped_df = grouped_df.rename(columns={'mean': 'Average Draft Position',
                                        'min': 'Highest Position',
                                        'max': 'Lowest Position',
                                        'count': '# Times Drafted'})

grouped_df = grouped_df.sort_values(by='Average Draft Position').reset_index()
grouped_df.to_csv("average_player_draft_position.csv", index=False)
grouped_df