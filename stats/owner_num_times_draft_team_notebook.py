""" Find players drafted by the same owner all time. """

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
# Get number of times owner drafts the same player
owner_team_counts_df = draft_df.value_counts(subset=['Owner Name', 'Team']).to_frame().reset_index()
owner_team_counts_df = owner_team_counts_df.rename(columns={0: '# Times Drafted'})
multi_df = pd.DataFrame()
for owner, df in owner_team_counts_df.groupby('Owner Name'):
    df = df.drop(columns='Owner Name').reset_index(drop=True)
    new_df = pd.DataFrame(columns=pd.MultiIndex.from_product([[owner], df.columns]))
    new_df[owner] = df
    multi_df = pd.concat([multi_df, new_df], axis=1)
multi_df.to_csv("owner_num_times_draft_team.csv", index=False)
multi_df