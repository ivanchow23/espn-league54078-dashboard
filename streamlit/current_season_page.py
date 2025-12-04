from daily_points import DailyPoints
import os
import plotly.graph_objects as go
import streamlit as st

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")
ESPN_FANTASY_API_ALL_PLAYERS_INFO_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "espn_fantasy_api_all_players_info_df.csv")

CURRENT_SEASON = 20252026

# ---------------------------------------- Helper Functions ---------------------------------------
def get_daily_points_cumulative_df(season):
    df = DailyPoints(ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH).get_cumulative_points_df(season)
    return df

def get_daily_points_norm_by_avg_df(season):
    df = DailyPoints(ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH).get_normalized_by_avg_df('appliedTotal', season)
    return df

def get_daily_points_plotly_fig(df, last_num_days=0):
    """ Helper function to return plotly figure to plot daily points.
        Set last_num_days = 0 to show plot for entire season. """
    # Filter
    if last_num_days != 0:
        latest_scoring_period = df['scoringPeriodId'].max()
        df = df[(df['scoringPeriodId'] >= (latest_scoring_period - last_num_days)) & (df['scoringPeriodId'] <= latest_scoring_period)]

    fig = go.Figure()
    for owner, owner_df in df.groupby('owner'):
        fig.add_trace(go.Scatter(x=owner_df['scoringPeriodId'], y=owner_df['appliedTotal'], name=owner))

    if last_num_days != 0:
        title_str = f"Total Points (Last {last_num_days} Days)"
    else:
        title_str = f"Total Points (Full Season)"

    fig.update_layout(title=title_str,
                      xaxis_title="Day Number",
                      yaxis_title=f"Fantasy Points",
                      margin=dict(t=50, b=80),
                      legend=dict(orientation='h', y=-0.2))
    return fig

def update_daily_stats_metrics(container, df, last_num_days=0):
    """ Updates various daily stats metrics in a container. Set last_num_days = 0
        for data for entire season. """
    # Filter
    latest_scoring_period = df['scoringPeriodId'].max()
    earliest_scoring_period = 1
    if last_num_days != 0:
        earliest_scoring_period = latest_scoring_period - last_num_days
        df = df[(df['scoringPeriodId'] >= (latest_scoring_period - last_num_days)) & (df['scoringPeriodId'] <= latest_scoring_period)]

    # League average
    # Take the latest scoring period data point and average across all owners
    num_owners = len(df['owner'].unique())
    league_avg_pts = round(df[df['scoringPeriodId'] == latest_scoring_period]['appliedTotal'].sum() / num_owners, 2)

    # Highest daily change across all owners
    highest_daily_pts = 0
    highest_daily_pts_owner = ""
    for owner, owner_df in df.groupby('owner'):
        max_daily_pts = round(owner_df['appliedTotal'].diff().max(), 2)
        max_daily_pts_idx = owner_df['appliedTotal'].diff().idxmax()
        day_num = owner_df['scoringPeriodId'].loc[max_daily_pts_idx]
        if max_daily_pts > highest_daily_pts:
            highest_daily_pts = max_daily_pts
            highest_daily_pts_owner = f"{owner} (Day {day_num})"
        elif max_daily_pts == highest_daily_pts:
            highest_daily_pts_owner += f"/{owner} (Day {day_num})"

    # Highest total change within the time period
    highest_total_change_pts = 0
    highest_total_change_owner = ""
    for owner, owner_df in df.groupby('owner'):
        start_pts = owner_df[owner_df['scoringPeriodId'] == earliest_scoring_period]['appliedTotal'].iloc[0]
        curr_pts = owner_df[owner_df['scoringPeriodId'] == latest_scoring_period]['appliedTotal'].iloc[0]
        change_pts = round(curr_pts - start_pts, 2)
        if change_pts > highest_total_change_pts:
            highest_total_change_pts = change_pts
            highest_total_change_owner = owner
        elif change_pts == highest_total_change_pts:
            highest_total_change_owner += f"/{owner}"

    container.metric(label="League Average", value=league_avg_pts, delta=None)
    container.metric(label="Highest Daily Change", value=highest_daily_pts, delta=highest_daily_pts_owner)
    container.metric(label=f"Highest Total Change", value=highest_total_change_pts, delta=highest_total_change_owner)

# -------------------------------------- Page content start ---------------------------------------
# Page configs
st.set_page_config(layout="wide")
st.markdown(f"<h3 style='text-align: center;'>ESPN League 54078 Dashboard - Current Season ({CURRENT_SEASON})</h2>", unsafe_allow_html=True)

# Load data
daily_points_df = get_daily_points_cumulative_df(season=CURRENT_SEASON)
daily_points_norm_by_avg_df = get_daily_points_norm_by_avg_df(season=CURRENT_SEASON)

# Daily plots stats containers
daily_pts_cols = st.columns([4, 1])
daily_pts_plot_container = daily_pts_cols[0].container(border=True, height="stretch", width="stretch")
daily_pts_stats_container = daily_pts_cols[1].container(border=True, height="stretch", width="stretch", vertical_alignment="center", horizontal_alignment="center")
daily_pts_num_days_select = daily_pts_stats_container.selectbox(label="Show For", options=["Last 7 Days", "Last 14 Days", "Last 30 Days", "Full Season"], key="daily_pts_num_days")

if daily_pts_num_days_select == "Full Season":
    daily_pts_plot_container.plotly_chart(get_daily_points_plotly_fig(daily_points_df))
    update_daily_stats_metrics(daily_pts_stats_container, daily_points_df)
elif daily_pts_num_days_select == "Last 7 Days":
    daily_pts_plot_container.plotly_chart(get_daily_points_plotly_fig(daily_points_df, last_num_days=7))
    update_daily_stats_metrics(daily_pts_stats_container, daily_points_df, last_num_days=7)
elif daily_pts_num_days_select == "Last 14 Days":
    daily_pts_plot_container.plotly_chart(get_daily_points_plotly_fig(daily_points_df, last_num_days=14))
    update_daily_stats_metrics(daily_pts_stats_container, daily_points_df, last_num_days=14)
elif daily_pts_num_days_select == "Last 30 Days":
    daily_pts_plot_container.plotly_chart(get_daily_points_plotly_fig(daily_points_df, last_num_days=30))
    update_daily_stats_metrics(daily_pts_stats_container, daily_points_df, last_num_days=30)