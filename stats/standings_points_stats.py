import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
STANDINGS_POINTS_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "standings_points_df.csv")

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

    def get_owner_first_season(self, owner):
        """ Returns an owner's first active season. """
        return self._standings_points_df[self._standings_points_df['Owner'] == owner]['Season'].min()

    def get_owner_last_season(self, owner):
        """ Returns an owner's last active season. """
        return self._standings_points_df[self._standings_points_df['Owner'] == owner]['Season'].max()

    def get_owner_average_rank(self, owner):
        """ Returns an owner's average rank for all seasons. """
        return round(self._standings_points_df[self._standings_points_df['Owner'] == owner]['RK'].mean(), 1)

    def get_owner_ranking_count(self, owner):
        """ Returns number of times an owner has placed in a certain position. """
        owner_df = self._standings_points_df[self._standings_points_df['Owner'] == owner].copy()
        owner_df['RK'] = owner_df['RK'].apply(self._number_ordinal)
        return owner_df['RK'].value_counts().sort_index()

    def get_owner_seasons_normalized_by_league_avg(self, owner):
        """ Returns dataframe of total points normalized by league average for
            all seasons for a given owner. Percent +/- Avg shows how much above/below
            the owner's total is compared to the league average. """
        owner_df = self._standings_points_df[self._standings_points_df['Owner'] == owner].copy()

        results = []
        for season in sorted(owner_df['Season'].unique()):
            season_df = self._standings_points_df[self._standings_points_df['Season'] == season]
            league_avg = season_df['TOT'].mean()

            owner_season_tot = owner_df[owner_df['Season'] == season]['TOT'].iloc[0]
            results.append({'Season': str(season),
                            '+/- Avg %': round(((owner_season_tot - league_avg) / league_avg) * 100, 2),
                            'Rank': owner_df[owner_df['Season'] == season]['RK'].iloc[0]})

        return pd.DataFrame(results)

    def get_owner_best_improved_season(self, owner):
        """ Returns information for an owner's best improved season. """
        owner_df = self._standings_points_df[self._standings_points_df['Owner'] == owner].copy()
        owner_df = owner_df.sort_values('Season').reset_index(drop=True)
        owner_df['RK Diff'] = owner_df['RK'].diff()
        idx = owner_df['RK Diff'].idxmin() # Get min value because lower rank is better

        season = str(owner_df.loc[idx, 'Season'])[:4] + "-" + str(owner_df.loc[idx, 'Season'])[4:]
        prev_rk = self._number_ordinal(owner_df.loc[idx - 1, 'RK'])
        rk = self._number_ordinal(owner_df.loc[idx, 'RK'])
        return season, prev_rk, rk

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
