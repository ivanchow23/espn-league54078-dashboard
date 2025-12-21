""" Drafted player points contribution stats. """
# %%
# Imports
#!/usr/bin/env python
import pandas as pd

class DraftPlayerPoints():
    def __init__(self, draft_df_path, daily_rosters_df_path):
        self._draft_df = pd.read_csv(draft_df_path)
        self._daily_rosters_df = pd.read_csv(daily_rosters_df_path)

    def get_df(self, owner, season):
        """ Return dataframe of draft player points data for given owner and season.
            Points earned for a player only applies for the time they were on the
            original owner's drafted team. """
        # Filter for season and owner
        season_daily_roster_df = self._daily_rosters_df[self._daily_rosters_df['season'] == season]
        season_daily_roster_df = season_daily_roster_df[season_daily_roster_df['owner'] == owner]
        season_draft_df = self._draft_df[self._draft_df['Season'] == season]
        season_draft_df = season_draft_df[season_draft_df['Owner Name'] == owner]

        # Omit slots where player is on bench or IR, which appear to be slots 7 and 8
        season_daily_roster_df = season_daily_roster_df[(season_daily_roster_df['lineupSlotId'] != 7) & (season_daily_roster_df['lineupSlotId'] != 8)]

        # Get sum of points for each player accumulated for the owner
        season_daily_roster_sum_df = season_daily_roster_df.groupby('id')['appliedTotal'].sum().reset_index()

        # Merge dataframes
        combined_df = season_draft_df.merge(season_daily_roster_sum_df, how='left', left_on='Player ID', right_on='id')
        combined_df['appliedTotal'] = combined_df['appliedTotal'].fillna(0)
        combined_df = combined_df[['Draft Number', 'Round Number', 'Player', 'appliedTotal']]
        return combined_df