#!/usr/bin/env python
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

class DailyPointsByPosition():
    def __init__(self, espn_fantasy_api_df_csv_path):
        """ Default constructor. """
        self._daily_rosters_df = pd.read_csv(espn_fantasy_api_df_csv_path)
        self._cols_of_interest = ['GP', 'appliedTotal', 'G', 'A', 'PPP', 'SHP', 'GWG', 'HAT', 'W', 'SO']

        # Dataframe of cumulative sums
        self._cumsum_df = self._get_cumsum_df()

    def get_seasons(self):
        """ Returns list of valid seasons contained in the data. """
        return self._daily_rosters_df['season'].unique()

    def get_plots_fig(self, season):
        """ Returns a figure of plots per position for the season. """
        # Filter for season
        season_cumsum_df = self._cumsum_df[self._cumsum_df['season'] == season]

        # Colour map
        colour_map = {owner: hex for owner, hex in zip(self._cumsum_df['owner'].unique(), px.colors.qualitative.Plotly)}

        # Generate multiple subplots in a figure
        fig = make_subplots(rows=len(self._cumsum_df['position'].unique()),
                            cols=1, shared_xaxes='all', vertical_spacing=0.05,
                            subplot_titles=sorted(self._cumsum_df['position'].unique()),
                            x_title="Scoring Period ID",
                            y_title="Normalized Points")

        # Plot cumulative points normalized by average
        for i, (_, pos_df) in enumerate(season_cumsum_df.groupby('position')):
            # Normalize
            normalized_df = pos_df.groupby('scoringPeriodId')['appliedTotal'].apply(lambda x: round(x / x.mean(), 2))
            normalized_df.index = normalized_df.index.droplevel('scoringPeriodId')
            pos_df['appliedTotal (norm. by avg)'] = normalized_df

            # Configurations to show proper shared legends
            # Do not show the legend for a subplot (unless it is the first subplot being made)
            show_legend = False
            if i == 0:
                show_legend = True

            for owner, owner_df in pos_df.groupby('owner'):
                fig.add_trace(go.Scatter(x=owner_df['scoringPeriodId'],
                                         y=owner_df['appliedTotal (norm. by avg)'],
                                         name=owner,
                                         line_color=colour_map[owner],
                                         legendgroup=owner, showlegend=show_legend),
                                         i + 1, 1)

        fig.update_layout(title=f"Daily Points by Position - Normalized by Average ({season})", height=1000)
        return fig

    def _get_cumsum_df(self):
        """ Get dataframe of cumulative sums derived from original raw dataframe. """
        # Omit slots where player is on bench or IR, which appear to be slots 7 and 8
        daily_rosters_non_ir_bench_df = self._daily_rosters_df[(self._daily_rosters_df['lineupSlotId'] != 7) & (self._daily_rosters_df['lineupSlotId'] != 8)]

        # Generate daily totals of each scoring period of each position of each owner
        # It seems like 3 = forwards, 4 = defence, 5 = goalies
        daily_totals_df = daily_rosters_non_ir_bench_df.groupby(['scoringPeriodId', 'owner', 'season', 'lineupSlotId'])[self._cols_of_interest].sum().reset_index()

        # Generate cumulative totals of each position of each scoring period of each owner of each season
        # Cumsum function does not keep original columns, so do some column manipulation to get original df columns but with cumsum values
        cumsum_df = daily_totals_df.copy(deep=True)
        cumsum_df[[f"{col}_cumsum" for col in self._cols_of_interest]] = daily_totals_df.groupby(['owner', 'season', 'lineupSlotId'])[self._cols_of_interest].cumsum()
        cumsum_df = cumsum_df.drop(columns=self._cols_of_interest)
        cumsum_df = cumsum_df.rename(columns={f"{col}_cumsum": col for col in self._cols_of_interest})

        # Remap lineup slot to position names
        cumsum_df['lineupSlotId'] = cumsum_df['lineupSlotId'].replace(3, "Forwards")
        cumsum_df['lineupSlotId'] = cumsum_df['lineupSlotId'].replace(4, "Defencemen")
        cumsum_df['lineupSlotId'] = cumsum_df['lineupSlotId'].replace(5, "Goalies")
        cumsum_df = cumsum_df.rename(columns={'lineupSlotId': 'position'})

        return cumsum_df