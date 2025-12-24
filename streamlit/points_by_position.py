#!/usr/bin/env python
import pandas as pd

class PointsByPosition():
    def __init__(self, espn_fantasy_api_df_csv_path):
        """ Default constructor. """
        self._daily_rosters_df = pd.read_csv(espn_fantasy_api_df_csv_path)
        self._cols_of_interest = ['GP', 'appliedTotal', 'G', 'A', 'PPP', 'SHP', 'GWG', 'HAT', 'W', 'SO']

        # Omit slots where player is on bench or IR, which appear to be slots 7 and 8
        self._daily_rosters_df = self._daily_rosters_df[(self._daily_rosters_df['lineupSlotId'] != 7) & (self._daily_rosters_df['lineupSlotId'] != 8)]

        # Remap lineup slot to position names
        self._daily_rosters_df['lineupSlotId'] = self._daily_rosters_df['lineupSlotId'].replace(3, "F")
        self._daily_rosters_df['lineupSlotId'] = self._daily_rosters_df['lineupSlotId'].replace(4, "D")
        self._daily_rosters_df['lineupSlotId'] = self._daily_rosters_df['lineupSlotId'].replace(5, "G")
        self._daily_rosters_df = self._daily_rosters_df.rename(columns={'lineupSlotId': 'position'})

    def get_seasons(self):
        """ Returns list of valid seasons contained in the data. """
        return self._daily_rosters_df['season'].unique()

    def get_df(self, season, last_num_days=0):
        """ Returns a dataframe of points by position stats for a given season
            in the last number of days. Set last_num_days = 0 for entire season. """
        # Filter for season
        season_df = self._daily_rosters_df[self._daily_rosters_df['season'] == season]

        # Filter for day number
        if last_num_days != 0:
            latest_scoring_period = season_df['scoringPeriodId'].max()
            # Note: Exclusive of the first day in range because we only want to include
            # daily data for after the day is finished
            season_df = season_df[(season_df['scoringPeriodId'] > (latest_scoring_period - last_num_days)) & (season_df['scoringPeriodId'] <= latest_scoring_period)]

        # Dataframe of totals and normalized data
        totals_df = self._get_totals_df(season_df)
        totals_df = pd.concat([totals_df, self._get_normalized_df(totals_df)], axis=1)

        # Get league average for the season
        num_owners = len(totals_df['owner'].unique())
        league_avg_stat_dict = {'Owner': "League Average",
                                'GP': int(round(totals_df['GP'].sum() / num_owners)),
                                'Points': round(totals_df['appliedTotal'].sum() / num_owners, 1)}

        for pos, pos_df in totals_df.groupby('position'):
            league_avg_stat_dict[f"{pos} (± avg)"] = round(pos_df['appliedTotal'].sum() / num_owners, 1)

        # Build dataframe table of stats by position for each owner
        stats_df = pd.DataFrame()
        for owner, owner_df in totals_df.groupby('owner'):
            stat_dict = {'Owner': owner,
                         'GP': int(owner_df['GP'].sum()),
                         'Points': round(owner_df['appliedTotal'].sum(), 2)}
            for pos, pos_df in owner_df.groupby('position'):
                pos_pts = round(pos_df['appliedTotal'].iloc[0], 2)
                pos_plus_minus_avg = round((pos_df['appliedTotal (norm. by avg)'].iloc[0] - 1.0) * 100, 1)
                stat_dict[f'{pos} (± avg)'] = f"{pos_pts} ({pos_plus_minus_avg}%)"
            stats_df = pd.concat([stats_df, pd.DataFrame([stat_dict])], ignore_index=True)
        stats_df = stats_df.sort_values(by='Points', ascending=False)

        # Put league average as first entry in table
        stats_df = pd.concat([pd.DataFrame([league_avg_stat_dict]), stats_df], ignore_index=True)
        return stats_df

    def _get_totals_df(self, df):
        """ Get dataframe of total sums derived from input dataframe. """
        # Generate daily totals of each scoring period of each position of each owner
        daily_totals_df = df.groupby(['scoringPeriodId', 'owner', 'season', 'position'])[self._cols_of_interest].sum().reset_index()

        # Sum all points over each season of each position
        total_sum_df = daily_totals_df.groupby(['owner', 'season', 'position'])[self._cols_of_interest].sum().reset_index()
        return total_sum_df

    def _get_normalized_df(self, df):
        """ Get normalized dataframe dervied from input dataframe. """
        normalized_df = df.groupby(['season', 'position'])[self._cols_of_interest].apply(lambda x: round(x / x.mean(), 3))
        normalized_df = normalized_df.rename(columns={col: f"{col} (norm. by avg)" for col in self._cols_of_interest})
        normalized_df.index = normalized_df.index.droplevel(['season', 'position'])
        return normalized_df