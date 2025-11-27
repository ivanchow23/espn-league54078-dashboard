#!/usr/bin/env python
from datetime import datetime
import dominate
from dominate.tags import *
from dominate.util import raw
from espn_nhlapi_analysis.espn_fantasy_api.daily_points import DailyPoints
from espn_nhlapi_analysis.espn_fantasy_api.points_by_position import PointsByPosition
from espn_nhlapi_analysis.espn_fantasy_api.daily_points_by_position import DailyPointsByPosition
from espn_nhlapi_analysis.espn_fantasy_api.player_with_different_owners import PlayerWithDifferentOwners
from espn_nhlapi_analysis.espn_fantasy_api.man_games_lost import ManGamesLost
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

SEASON = 20252026
ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")
ESPN_FANTASY_API_ALL_PLAYERS_INFO_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "espn_fantasy_api_all_players_info_df.csv")

class HtmlDashboardGenerator():
    def __init__(self, html_output_path=os.path.join(SCRIPT_DIR, "index.html")):
        """ Default constructor. """
        self._html_output_path = html_output_path

        # Set-up HTML document
        self._doc = self._setup_html_doc()

    def get_doc(self):
        """ Returns a reference to the HTML document. """
        return self._doc

    def generate(self):
        """ Generate the HTML dashboard page. """
        with open(self._html_output_path, 'wb') as html_file:
            html_doc_string = self._doc.render()
            html_doc_encoded = html_doc_string.encode('utf-8')
            html_file.write(html_doc_encoded)

    def _setup_html_doc(self):
        """ Sets up an HTML document. """
        doc = dominate.document(title="ESPN HTML Dashboard")
        dt_str = datetime.now().strftime(r"%m/%d/%Y %H:%M")

        # Enable plotly interactive graphs
        with doc.head:
            plotly_js = ""
            with open(os.path.join(SCRIPT_DIR, "plotly-2.27.0.min.js"), 'r', encoding='utf-8') as plotly_js_file:
                plotly_js = plotly_js_file.read()
            script(raw(plotly_js))

        # Add title headers
        doc.add(h2(f"ESPN League 54078 Dashboard", align='center', style="font-family:tahoma; font-size:28px; color:black;"))
        doc.add(p(f"Generated: {dt_str}", align='center', style="font-family:tahoma; color:black;"))

        return doc

if __name__ == "__main__":
    dashboard = HtmlDashboardGenerator()
    doc = dashboard.get_doc()

    dp = DailyPoints(ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH)
    pbp = PointsByPosition(ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH)
    dpbp = DailyPointsByPosition(ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH)
    pwdo = PlayerWithDifferentOwners(ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH, ESPN_FANTASY_API_ALL_PLAYERS_INFO_CSV_PATH)
    mgl = ManGamesLost(ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH)

    dp_fig = dp.get_cumulative_points_plot(key="appliedTotal", season=SEASON)
    dp_norm_avg_fig = dp.get_cumulative_points_norm_by_avg_plot(key="appliedTotal", season=SEASON)
    dp_norm_first_fig = dp.get_cumulative_points_norm_by_first_plot(key="appliedTotal", season=SEASON)
    pbp_fig = pbp.get_stats_table(season=SEASON)
    dpbp_fig = dpbp.get_plots_fig(season=SEASON)
    pwdo_fig = pwdo.get_table_fig(season=SEASON)
    mgl_fig = mgl.get_table_fig(season=SEASON)

    dp_html = dp_fig.to_html(include_plotlyjs=False, full_html=False)
    dp_norm_avg_html = dp_norm_avg_fig.to_html(include_plotlyjs=False, full_html=False)
    dp_norm_first_html = dp_norm_first_fig.to_html(include_plotlyjs=False, full_html=False)
    pbp_html = pbp_fig.to_html(include_plotlyjs=False, full_html=False)
    dpbp_html = dpbp_fig.to_html(include_plotlyjs=False, full_html=False)
    pwdo_html = pwdo_fig.to_html(include_plotlyjs=False, full_html=False)
    mgl_html = mgl_fig.to_html(include_plotlyjs=False, full_html=False)

    with doc:
        with div() as d:
            raw(dp_html)
            raw(dp_norm_avg_html)
            raw(dp_norm_first_html)
            raw(pbp_html)
            raw(dpbp_html)
            raw(pwdo_html)
            raw(mgl_html)

    dashboard.generate()