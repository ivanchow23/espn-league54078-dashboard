from daily_points import DailyPoints
from draft_player_points import DraftPlayerPoints
from draft_stats import DraftStats
import os
import pandas as pd
from player_with_different_owners import PlayerWithDifferentOwners
from points_by_position import PointsByPosition
import plotly
import plotly.graph_objects as go
import streamlit as st

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DRAFT_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "draft_df.csv")
ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")
ESPN_FANTASY_API_ALL_PLAYERS_INFO_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "espn_fantasy_api_all_players_info_df.csv")

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

    # Create figure
    fig = go.Figure()

    # Add league average line
    fig.add_trace(go.Scatter(x=df[df['owner'] == "League Average"]['scoringPeriodId'],
                             y=df[df['owner'] == "League Average"]['appliedTotal'],
                             line=dict(color='grey', width=4, dash='dot'),
                             mode='lines',
                             name="League Avg"))

    # Add lines for each owner
    default_colours = plotly.colors.qualitative.Plotly
    for i, (owner, owner_df) in enumerate(df.groupby('owner')):
        # Already plotted league average line
        if owner == "League Average":
            continue
        fig.add_trace(go.Scatter(x=owner_df['scoringPeriodId'],
                                 y=owner_df['appliedTotal'],
                                 line=dict(color=default_colours[i]),
                                 name=owner))

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
    df = df[df['owner'] != "League Average"]

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

    container.metric(label="Highest Daily Change", value=highest_daily_pts, delta=highest_daily_pts_owner)
    container.metric(label=f"Highest Total Change", value=highest_total_change_pts, delta=highest_total_change_owner)

def get_draft_birth_country_fig(series):
    """ Helper function to return a plotly figure for draft birth country data. """
    wedge_colour_map={"CAN": '#cd5c5c', "USA": '#4169e1', "RUS/USSR": '#fffafa', "SWE": '#ffd700',
                      "FIN": '#000080', "CZE": '#add8e6', "SVK": '#add8e6', "Czechoslovakia": '#add8e6',
                      "SUI": '#b22222', "DEN": '#911b1b', "NOR": '#da2a2a', "GER": '#696969'}

    fig = go.Figure()
    wedge_colours = [wedge_colour_map[index] if index in wedge_colour_map else "darkgray" for index in series.index]
    fig.add_trace(go.Pie(labels=series.index, values=series.values, marker_colors=wedge_colours,
                         hole=0.35, pull=[0.075 if i == 0 else 0.03 for i, _ in enumerate(series.values)]))
    fig.update_layout(title="Player Birth Countries", margin=dict(t=50, b=50), height=300)
    return fig

def get_draft_age_fig(series):
    """ Helper function to return a plotly figure for draft age data. """
    # Stats
    try:
        mean = round(series.index.to_series().mean(), 1)
    except ValueError:
        mean = 0
    try:
        min = int(series.index.to_series().min())
    except ValueError:
        min = 0
    try:
        max = int(series.index.to_series().max())
    except ValueError:
        max = 0

    fig = go.Figure()
    fig.add_trace(go.Bar(x=series.index, y=series.values))
    fig.update_layout(title=f"Player Age", xaxis_title=f"Age (Min = {min} | Mean = {mean} | Max = {max})",
                      yaxis_title="# of Picks", margin=dict(t=50, b=10), height=300)
    return fig

def get_draft_points_fig(df):
    """ Helper function to return a plotly figure for player points vs. draft data. """
    # Plot bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['Round Number'], y=df['appliedTotal'], hovertext=df['Player'], marker_color="#3ECA56"))
    fig.update_layout(title=f"Points Earned for Drafted Owner<br><i>Hey, who's this guy?<i>",
                      xaxis_title="Draft Number", yaxis_title="Points", margin=dict(t=50, b=10), height=300)
    return fig

# -------------------------------------- Page content start ---------------------------------------
# Page configs
st.set_page_config(layout="wide")
st.markdown(f"<h3 style='text-align: center;'>ESPN League 54078 Dashboard</h2>", unsafe_allow_html=True)

# Raw data
daily_points_df = pd.read_csv(ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH)

# Select season to show
st.markdown("#### Season to Display")
seasons = sorted(daily_points_df['season'].unique(), reverse=True)
seasons_select_options = sorted(daily_points_df['season'].astype(str).unique(), reverse=True)
seasons_select_options = [season[:4] + "-" + season[4:] for season in seasons_select_options]
seasons_select_options[0] = f"{seasons_select_options[0]} (Current)"

season_select_cols = st.columns([1, 3])
selected_season_str = season_select_cols[0].selectbox(label="Show Season", options=seasons_select_options, key=seasons, label_visibility='collapsed')
selected_season_str = selected_season_str.replace("-", "")
if "Current" in selected_season_str:
    selected_season = seasons[seasons.index(int(selected_season_str.strip(" (Current)")))]
else:
    selected_season = seasons[seasons.index(int(selected_season_str))]

# Daily plots stats containers
st.markdown("#### Daily Points Stats")
season_daily_points_df = get_daily_points_cumulative_df(season=selected_season)
daily_pts_cols = st.columns([4, 1])
daily_pts_plot_container = daily_pts_cols[0].container(border=True, height="stretch", width="stretch")
daily_pts_stats_container = daily_pts_cols[1].container(border=True, height="stretch", width="stretch", vertical_alignment="top", horizontal_alignment="center")
daily_pts_num_days_select = daily_pts_stats_container.selectbox(label="Show For", options=["Last 7 Days", "Last 14 Days", "Last 30 Days", "Full Season"], key="daily_pts_num_days")

if daily_pts_num_days_select == "Full Season":
    daily_pts_plot_container.plotly_chart(get_daily_points_plotly_fig(season_daily_points_df))
    update_daily_stats_metrics(daily_pts_stats_container, season_daily_points_df)
elif daily_pts_num_days_select == "Last 7 Days":
    daily_pts_plot_container.plotly_chart(get_daily_points_plotly_fig(season_daily_points_df, last_num_days=7))
    update_daily_stats_metrics(daily_pts_stats_container, season_daily_points_df, last_num_days=7)
elif daily_pts_num_days_select == "Last 14 Days":
    daily_pts_plot_container.plotly_chart(get_daily_points_plotly_fig(season_daily_points_df, last_num_days=14))
    update_daily_stats_metrics(daily_pts_stats_container, season_daily_points_df, last_num_days=14)
elif daily_pts_num_days_select == "Last 30 Days":
    daily_pts_plot_container.plotly_chart(get_daily_points_plotly_fig(season_daily_points_df, last_num_days=30))
    update_daily_stats_metrics(daily_pts_stats_container, season_daily_points_df, last_num_days=30)

# Points by position stats containers
st.markdown("#### Points by Position Stats")
points_by_position_num_cols_per_row = 4
points_by_position_df = PointsByPosition(ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH).get_df(season=selected_season)

league_avg_pts = round(points_by_position_df['Total Points'].mean(), 2)
league_f_avg_pts = round(points_by_position_df['Forwards'].mean(), 2)
league_d_avg_pts = round(points_by_position_df['Defencemen'].mean(), 2)
league_g_avg_pts = round(points_by_position_df['Goalies'].mean(), 2)

# Write cells for all owners plus league average as the first cell
num_owners = len(points_by_position_df['Owner'].unique())
for i in range(0, num_owners + 1, points_by_position_num_cols_per_row):
    cols = st.columns(points_by_position_num_cols_per_row)
    for j, col in enumerate(cols):
        container = col.container(border=True, height="stretch", width="stretch", vertical_alignment="top", horizontal_alignment="center")

        # Write league average for first cell
        if i + j == 0:
            container.write("League Average")
            container.metric("Total", value=league_avg_pts, delta=None)
            container.metric("Forwards", value=league_f_avg_pts, delta=None)
            container.metric("Defencemen", value=league_d_avg_pts, delta=None)
            container.metric("Goalies", value=league_g_avg_pts, delta=None)
        else:
            idx = i + j - 1
            if idx >= num_owners:
                break
            df = points_by_position_df.iloc[[idx]]
            container.write(f"{idx + 1} - {df['Owner'].iloc[0]}")
            container.metric("Total", value=df['Total Points'].iloc[0], delta=None)
            container.metric("Forwards", value=df['Forwards'].iloc[0], delta=df['Forwards +/- Avg'].iloc[0])
            container.metric("Defencemen", value=df['Defencemen'].iloc[0], delta=df['Defencemen +/- Avg'].iloc[0])
            container.metric("Goalies", value=df['Goalies'].iloc[0], delta=df['Goalies +/- Avg'].iloc[0])

# Players with different owners stats containers
st.markdown("#### Players with Different Owners Stats")
st.markdown("##### _\"Roope Stats\"_")
players_diff_owners_num_cols_per_row = 3
players_diff_owners_dicts = PlayerWithDifferentOwners(ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH, ESPN_FANTASY_API_ALL_PLAYERS_INFO_CSV_PATH).get_dicts(selected_season)

for i in range(0, len(players_diff_owners_dicts), players_diff_owners_num_cols_per_row):
    cols = st.columns(players_diff_owners_num_cols_per_row)
    for j, col in enumerate(cols):
        idx = i + j
        if idx >= len(players_diff_owners_dicts):
            break

        player_dict = players_diff_owners_dicts[idx]
        player_container = col.container(border=True, height="stretch", width="stretch", vertical_alignment="top", horizontal_alignment="center")
        player_container.image(f"https://a.espncdn.com/i/headshots/nhl/players/full/{player_dict['Player ID']}.png", caption=player_dict['Player Name'], width=200)
        df = pd.DataFrame(player_dict['Owners'])

        # Cast to string type to somehow make cols appear left-aligned
        # https://discuss.streamlit.io/t/st-dataframe-numbers-left-aligned/84901/2
        df = df.astype(str)
        player_container.dataframe(df, hide_index=True)

# Draft stats container
st.markdown("#### Draft Stats")
draft_stats = DraftStats(DRAFT_CSV_PATH)
draft_player_points_stats = DraftPlayerPoints(DRAFT_CSV_PATH, ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH)
draft_stats_owners = draft_stats.get_unique_owners()
for owner in draft_stats_owners:
    container = st.container(border=True, height="stretch", width="stretch", vertical_alignment="center", horizontal_alignment="center")
    container.markdown(f"<h4 style='text-align: left;'>{owner}</h4>", unsafe_allow_html=True)
    container_cols = container.columns([0.1, 2, 0.25, 2, 0.25, 2.5, 0.1])
    container_cols[1].plotly_chart(get_draft_birth_country_fig(draft_stats.get_draft_birth_country_data(owner, selected_season)))
    container_cols[3].plotly_chart(get_draft_age_fig(draft_stats.get_draft_player_age_data(owner, selected_season)))
    container_cols[5].plotly_chart(get_draft_points_fig(draft_player_points_stats.get_df(owner, selected_season)))