import os
import pandas as pd

STANDINGS_POINTS_CSV_PATH = os.path.join("..", "docs", "data", "standings_points_df.csv")

class StandingsPointsStats():
    def __init__(self):
        """ Default constructor. """
        self._standings_points_df = pd.read_csv(STANDINGS_POINTS_CSV_PATH)

    def get_unique_owners(self):
        """ Get list of unique owners. """
        return sorted(self._standings_points_df['Owner'].unique())

    def get_owner_num_seasons_active(self, owner):
        """ Returns number of seasons active for an owner. """
        return len(self._standings_points_df[self._standings_points_df['Owner'] == owner])

    def get_owner_ranking_count(self, owner):
        """ Returns number of times an owner has placed in a certain position. """
        owner_df = self._standings_points_df[self._standings_points_df['Owner'] == owner].copy()
        owner_df['RK'] = owner_df['RK'].apply(self._number_ordinal)
        return owner_df['RK'].value_counts().sort_index()

    def _number_ordinal(self, val):
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
