import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Workaround for import stats to deploy on streamlit app
# This is because it currently uses uv pip install on the requirements.txt file
# Does not have the same package management as using uv sync on the pyproject.toml
import sys
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, ".."))

from stats.draft_stats import DraftStats
from stats.standings_points_stats import StandingsPointsStats

draft_stats = DraftStats()
standing_points_stats = StandingsPointsStats()

# ---------------------------------------- Helper Functions ---------------------------------------
def get_rankings_fig(owner):
    """ Helper function to return a plotly figure of rankings data. """
    ranking_counts = standing_points_stats.get_owner_ranking_count(owner)
    wedge_colour_map = {"1st": '#ffd700', "2nd": '#b0c4de', "3rd": '#d2b48c'}
    wedge_colours = [wedge_colour_map[index] if index in wedge_colour_map else "darkgray" for index in ranking_counts.index]

    fig = go.Figure()
    fig.add_trace(go.Pie(labels=ranking_counts.index, values=ranking_counts, name=owner, marker_colors=wedge_colours,
                         hole=0.25, pull=0.025, textinfo='label+value', textposition='auto'))
    fig.update_layout(title="Standing Rankings", margin=dict(t=50, b=20), height=300, showlegend=False)
    return fig

def get_draft_positions_fig(owner):
    """ Helper function to return a plotly figure of draft positions data. """
    position_counts = draft_stats.get_owner_draft_position_data(owner)
    wedge_colours = ["lightblue" for _ in position_counts.index]

    fig = go.Figure()
    fig.add_trace(go.Pie(labels=position_counts.index, values=position_counts, name=owner, marker_colors=wedge_colours, hole=0.25, pull=0.025, textinfo='label+value', textposition='auto'))
    fig.update_layout(title="Draft Positions", margin=dict(t=50, b=20), height=300, showlegend=False)
    return fig

def get_seasons_normalized_by_league_avg_fig(owner):
    """ Helper function to return a plotly figure of an owner's season stats
        normalized by league average with bar chart of +/- Avg % and line chart of Rank. """
    df = standing_points_stats.get_owner_seasons_normalized_by_league_avg(owner)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df['Season'], y=df['+/- Avg %'], name='+/- Avg %',
                         marker_color=['#3ECA56' if x >= 0 else "#EE4B4B" for x in df['+/- Avg %']]))
    fig.add_trace(go.Scatter(x=df['Season'], y=df['Rank'], name='Rank', mode='lines+markers'), secondary_y=True)

    fig.update_layout(
        title="Season Performance vs. League Average",
        xaxis=dict(title="Season", type='category'),
        yaxis=dict(title='+/- Avg %', side='left', range=[-15, 15]),
        yaxis2=dict(title='Rank', overlaying='y', side='right', range=[8, 0], autorange=False),
        margin=dict(t=50, b=20),
        height=300,
        hovermode='x unified',
        legend=dict(x=1.1, y=1.25, xanchor='right', yanchor='top'))

    return fig

def get_draft_birth_country_fig(owner):
    """ Helper function to return a plotly figure for draft birth country data. """
    series = draft_stats.get_draft_birth_country_data(owner)

    wedge_colour_map={"CAN": '#cd5c5c', "USA": '#4169e1', "RUS/USSR": '#fffafa', "SWE": '#ffd700',
                      "FIN": '#000080', "CZE": '#add8e6', "SVK": '#add8e6', "Czechoslovakia": '#add8e6',
                      "SUI": '#b22222', "DEN": '#911b1b', "NOR": '#da2a2a', "GER": '#696969'}

    fig = go.Figure()
    wedge_colours = [wedge_colour_map[index] if index in wedge_colour_map else "darkgray" for index in series.index]
    fig.add_trace(go.Pie(labels=series.index, values=series.values, marker_colors=wedge_colours,
                         hole=0.35, pull=[0.075 if i == 0 else 0.03 for i, _ in enumerate(series.values)], textinfo='label+value', textposition='auto'))
    fig.update_layout(title="Player Birth Countries", margin=dict(t=50, b=50), height=350, showlegend=False)
    return fig

def get_draft_conference_fig(owner):
    """ Helper function to return a plotly figure for draft conference data. """
    series = draft_stats.get_draft_player_conference_data(owner)

    wedge_colour_map = {"Eastern": "#fc4b4b", "Western": "#206eff"}
    wedge_colours = [wedge_colour_map[index] if index in wedge_colour_map else "darkgray" for index in series.index]

    fig = go.Figure()
    fig.add_trace(go.Pie(labels=series.index, values=series.values, marker_colors=wedge_colours, hole=0.35, pull=0.03, textinfo='label+value', textposition='auto'))
    fig.update_layout(title="Drafted Conference", margin=dict(t=50, b=50), height=350, showlegend=False)
    return fig

def get_draft_age_fig(owner):
    """ Helper function to return a plotly figure for draft age data. """
    series = draft_stats.get_draft_player_age_data(owner)

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
                      yaxis_title="# of Picks", margin=dict(t=50, b=10), height=350)
    return fig

# -------------------------------------- Page content start ---------------------------------------
# Page configs
st.set_page_config(layout="wide")
st.markdown(f"<h3 style='text-align: center;'>Owner Profiles</h2>", unsafe_allow_html=True)

# Select box
select_options_container = st.container()
select_options_cols = select_options_container.columns([1, 1, 1, 1])

# Custom CSS to make selectbox a sticky header
# Reference: https://discuss.streamlit.io/t/is-it-possible-to-create-a-sticky-header/33145 and Copilot
select_options_container.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)
select_options_container.markdown(
    """
<style>
    div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
        position: sticky;
        top: 3rem;
        margin-bottom: -0.75rem;
        background: transparent;                     /* show the page background */
        color: inherit;                              /* use theme text color */
        backdrop-filter: saturate(180%) blur(100px); /* optional visual polish */
        z-index: 999;
    }
</style>
    """,
    unsafe_allow_html=True
)

# Select owners to show
owners_select_options = sorted(draft_stats.get_unique_owners())
select_options_cols[0].markdown("#### Owner")
selected_owner = select_options_cols[0].selectbox(label="Owner", options=owners_select_options, key="owners", label_visibility='collapsed')

# Summary stats container
st.markdown("#### Summary Stats")
container = st.container(border=True, horizontal=True)
container.metric(label="Seasons Played", value=standing_points_stats.get_owner_num_seasons_active(selected_owner), delta_arrow="off",
                 delta=f"{standing_points_stats.get_owner_first_season(selected_owner)} - {standing_points_stats.get_owner_last_season(selected_owner)}")
s, p, c = standing_points_stats.get_owner_best_improved_season(selected_owner)
container.metric(label="Best Improved Season", value=s, delta=f"{p} to {c}")
container.metric(label="Average Rank", value=standing_points_stats.get_owner_average_rank(selected_owner))
container.metric(label="Average vs. League Average",
                 value=f"{round(standing_points_stats.get_owner_seasons_normalized_by_league_avg(selected_owner)['+/- Avg %'].mean(), 2)}%")

# Summary stats charts
container = st.container(border=False, height="stretch", width="stretch", vertical_alignment="center", horizontal_alignment="center")
container_cols = container.columns([1, 0.5, 0.5])
container_cols[0].container(border=True).plotly_chart(get_seasons_normalized_by_league_avg_fig(selected_owner))
container_cols[1].container(border=True).plotly_chart(get_rankings_fig(selected_owner))
container_cols[2].container(border=True).plotly_chart(get_draft_positions_fig(selected_owner))

# Draft stats container
st.markdown("#### Draft Stats")
container = st.container(border=True)
container_cols = container.columns(3)
container_cols[0].plotly_chart(get_draft_birth_country_fig(selected_owner))
container_cols[1].plotly_chart(get_draft_conference_fig(selected_owner))
container_cols[2].plotly_chart(get_draft_age_fig(selected_owner))

container = st.container(border=True)
container.markdown("###### Top Players Drafted")
container = container.container(border=False, horizontal_alignment="left", horizontal=True)
players_data = draft_stats.get_owner_top_drafted_players(selected_owner, num_players=10)
for p in players_data:
    container.image(f"https://a.espncdn.com/i/headshots/nhl/players/full/{p['Player ID']}.png",
                    caption=f"{p['Player']} ({p['Count']})", width=150)