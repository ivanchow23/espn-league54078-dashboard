#!/usr/bin/env python
import pandas as pd
import plotly.graph_objects as go

class DailyPoints():
    def __init__(self, espn_fantasy_api_df_csv_path):
        """ Default constructor. """
        self._daily_rosters_df = pd.read_csv(espn_fantasy_api_df_csv_path)
        self._cols_of_interest = ['GP', 'appliedTotal', 'G', 'A', 'PPP', 'SHP', 'GWG', 'HAT', 'W', 'SO']

        # Dataframe of cumulative sums
        self._cumsum_df = self._get_cumsum_df()

    def get_seasons(self):
        """ Returns list of valid seasons contained in the data. """
        return self._daily_rosters_df['season'].unique()

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
        return cumsum_df