#!/usr/bin/env python
import os
import pandas as pd
import plotly.graph_objects as go

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")

class DailyPoints():
    def __init__(self):
        """ Default constructor. """
        self._daily_rosters_df = pd.read_csv(ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH)
        self._cols_of_interest = ['GP', 'appliedTotal', 'G', 'A', 'PPP', 'SHP', 'GWG', 'HAT', 'W', 'SO']

        # Dataframe of cumulative sums
        self._cumsum_df = self._get_cumsum_df()

    def get_cumulative_points_df(self, season):
        """ Returns dataframe for cumulative points for given season. """
        return self._cumsum_df[self._cumsum_df['season'] == season]

    def get_normalized_by_avg_df(self, key, season):
        """ Returns dataframe for normalized by average for given season for
            the given stat (key). """
        # Filter for season
        season_df = self._cumsum_df[self._cumsum_df['season'] == season]

        # Normalize
        normalized_df = season_df.groupby('scoringPeriodId')[key].apply(lambda x: round(x / x.mean(), 3))
        normalized_df.index = normalized_df.index.droplevel('scoringPeriodId')
        season_df[f'{key} (norm. by avg)'] = normalized_df
        return season_df

    def get_seasons(self):
        """ Returns list of valid seasons contained in the data. """
        return sorted(list(self._daily_rosters_df['season'].unique()))

    def get_simulated_points_df(self, season, scoring_values, actual_scoring_values):
        """Return final team totals for a season using custom scoring values."""
        season_df = self._daily_rosters_df[self._daily_rosters_df['season'] == season]
        active_rosters_df = season_df[(season_df['lineupSlotId'] != 7) & (season_df['lineupSlotId'] != 8)].copy()

        for stat in scoring_values:
            active_rosters_df[stat] = pd.to_numeric(active_rosters_df[stat], errors='coerce').fillna(0)

        active_rosters_df['simulatedPoints'] = sum(
            (active_rosters_df[stat] / actual_scoring_values[stat]) * value
            for stat, value in scoring_values.items()
        )
        totals_df = active_rosters_df.groupby('owner')['simulatedPoints'].sum().reset_index()
        return totals_df.sort_values('simulatedPoints', ascending=False).reset_index(drop=True)

    def get_simulated_points_by_position_df(self, season, scoring_values, actual_scoring_values):
        """Return simulated final points grouped by owner and roster position."""
        season_df = self._daily_rosters_df[self._daily_rosters_df['season'] == season]
        active_rosters_df = season_df[season_df['lineupSlotId'].isin([3, 4, 5])].copy()

        for stat in scoring_values:
            active_rosters_df[stat] = pd.to_numeric(active_rosters_df[stat], errors='coerce').fillna(0)

        active_rosters_df['simulatedPoints'] = sum(
            (active_rosters_df[stat] / actual_scoring_values[stat]) * value
            for stat, value in scoring_values.items()
        )
        active_rosters_df['position'] = active_rosters_df['lineupSlotId'].map({3: 'Forwards', 4: 'Defense', 5: 'Goalies'})
        return active_rosters_df.groupby(['owner', 'position'])['simulatedPoints'].sum().unstack(fill_value=0).reset_index()

    def get_cumulative_points_plot(self, key, season):
        """ Get plot of raw cumulative points for the given season. """
        # Filter for season
        season_df = self._cumsum_df[self._cumsum_df['season'] == season]

        # Plot
        fig = go.Figure()
        for owner, owner_df in season_df.groupby('owner'):
            fig.add_trace(go.Scatter(x=owner_df['scoringPeriodId'], y=owner_df[key], name=owner))
        fig.update_layout(title=f"Cumulative Total Points ({key}) ({season})",
                          xaxis_title="Scoring Period ID",
                          yaxis_title=f"Total Points ({key})")
        return fig

    def get_cumulative_points_norm_by_avg_plot(self, key, season):
        """ Get plot of cumulative points (normalized by the average) for the given season. """
        # Filter for season
        season_df = self._cumsum_df[self._cumsum_df['season'] == season]

        # Normalize
        normalized_df = season_df.groupby('scoringPeriodId')[key].apply(lambda x: round(x / x.mean(), 3))
        normalized_df.index = normalized_df.index.droplevel('scoringPeriodId')
        season_df[f'{key} (norm. by avg)'] = normalized_df

        # Plot
        fig = go.Figure()
        for owner, owner_df in season_df.groupby('owner'):
            fig.add_trace(go.Scatter(x=owner_df['scoringPeriodId'], y=owner_df[f'{key} (norm. by avg)'], name=owner))
        fig.update_layout(title=f"Cumulative Total Points ({key}) - Normalized by Average ({season})",
                         xaxis_title="Scoring Period ID",
                         yaxis_title=f"Total Points ({key})")
        return fig

    def get_cumulative_points_norm_by_first_plot(self, key, season):
        """ Get plot of cumulative points (normalized by first place) for the given season. """
        # Filter for season
        season_df = self._cumsum_df[self._cumsum_df['season'] == season]

        # Normalize
        normalized_df = season_df.groupby('scoringPeriodId')[key].apply(lambda x: round(x / x.max(), 3))
        normalized_df.index = normalized_df.index.droplevel('scoringPeriodId')
        season_df[f'{key} (norm. by first)'] = normalized_df

        # Plot
        fig = go.Figure()
        for owner, owner_df in season_df.groupby('owner'):
            fig.add_trace(go.Scatter(x=owner_df['scoringPeriodId'], y=owner_df[f'{key} (norm. by first)'], name=owner))
        fig.update_layout(title=f"Cumulative Total Points ({key}) - Normalized by First ({season})",
                         xaxis_title="Scoring Period ID",
                         yaxis_title=f"Total Points ({key})")
        return fig

    def _get_cumsum_df(self):
        """ Get dataframe of cumulative sums derived from original raw dataframe. """
        # Generate daily totals of each scoring period of each owner of each season
        # Omit slots where player is on bench or IR, which appear to be slots 7 and 8
        daily_rosters_non_ir_bench_df = self._daily_rosters_df[(self._daily_rosters_df['lineupSlotId'] != 7) & (self._daily_rosters_df['lineupSlotId'] != 8)]
        daily_totals_df = daily_rosters_non_ir_bench_df.groupby(['scoringPeriodId', 'owner', 'season'])[self._cols_of_interest].sum().reset_index()

        # Generate cumulative totals of each scoring period of each owner of each season
        # Cumsum function does not keep original columns, so do some column manipulation to get original df columns but with cumsum values
        cumsum_df = daily_totals_df.copy(deep=True)
        cumsum_df[[f"{col}_cumsum" for col in self._cols_of_interest]] = daily_totals_df.groupby(['owner', 'season'])[self._cols_of_interest].cumsum()
        cumsum_df = cumsum_df.drop(columns=self._cols_of_interest)
        cumsum_df = cumsum_df.rename(columns={f"{col}_cumsum": col for col in self._cols_of_interest})

        # Insert league average data
        league_avg_df = cumsum_df.groupby(['scoringPeriodId', 'season'])[self._cols_of_interest].mean().round(2).reset_index()
        league_avg_df['owner'] = "League Average"
        cumsum_df = pd.concat([cumsum_df, league_avg_df])
        return cumsum_df