import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Workaround for import stats to deploy on streamlit app
# This is because it currently uses uv pip install on the requirements.txt file
# Does not have the same package management as using uv sync on the pyproject.toml
import sys
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, ".."))

from stats.draft_stats import DraftStats

DRAFT_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "draft_df.csv")

draft_stats = DraftStats(DRAFT_CSV_PATH)

# ---------------------------------------- Helper Functions ---------------------------------------
def get_draft_birth_country_fig(owner):
    """ Helper function to return a plotly figure for draft birth country data. """
    series = draft_stats.get_draft_birth_country_data(owner)

    wedge_colour_map={"CAN": '#cd5c5c', "USA": '#4169e1', "RUS/USSR": '#fffafa', "SWE": '#ffd700',
                      "FIN": '#000080', "CZE": '#add8e6', "SVK": '#add8e6', "Czechoslovakia": '#add8e6',
                      "SUI": '#b22222', "DEN": '#911b1b', "NOR": '#da2a2a', "GER": '#696969'}

    fig = go.Figure()
    wedge_colours = [wedge_colour_map[index] if index in wedge_colour_map else "darkgray" for index in series.index]
    fig.add_trace(go.Pie(labels=series.index, values=series.values, marker_colors=wedge_colours,
                         hole=0.35, pull=[0.075 if i == 0 else 0.03 for i, _ in enumerate(series.values)]))
    fig.update_layout(title="Player Birth Countries", margin=dict(t=50, b=50), height=400)
    return fig

def get_draft_conference_fig(owner):
    """ Helper function to return a plotly figure for draft conference data. """
    series = draft_stats.get_draft_player_conference_data(owner)

    wedge_colour_map = {"Eastern": "#fc4b4b", "Western": "#206eff"}
    wedge_colours = [wedge_colour_map[index] if index in wedge_colour_map else "darkgray" for index in series.index]

    fig = go.Figure()
    fig.add_trace(go.Pie(labels=series.index, values=series.values, marker_colors=wedge_colours, hole=0.35, pull=0.03))
    fig.update_layout(title="Drafted Conference", margin=dict(t=50, b=50), height=400)
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
                      yaxis_title="# of Picks", margin=dict(t=50, b=10), height=400)
    return fig

# -------------------------------------- Page content start ---------------------------------------
# Page configs
st.set_page_config(layout="wide")
st.markdown(f"<h3 style='text-align: center;'>Owner Profiles</h2>", unsafe_allow_html=True)

# Read data
draft_df = pd.read_csv(DRAFT_CSV_PATH)

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
owners_select_options = sorted(draft_df['Owner Name'].unique())
select_options_cols[0].markdown("#### Owner")
selected_owner = select_options_cols[0].selectbox(label="Owner", options=owners_select_options, key="owners", label_visibility='collapsed')

# Draft stats container
st.markdown("#### Draft Stats")
container = st.container(border=True, height="stretch", width="stretch", vertical_alignment="center", horizontal_alignment="center")
container_cols = container.columns([1, 0.9, 1])
container_cols[0].plotly_chart(get_draft_birth_country_fig(selected_owner))
container_cols[1].plotly_chart(get_draft_conference_fig(selected_owner))
container_cols[2].plotly_chart(get_draft_age_fig(selected_owner))