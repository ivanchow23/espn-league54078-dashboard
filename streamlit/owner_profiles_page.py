import os
import pandas as pd
import streamlit as st

# Workaround for import stats to deploy on streamlit app
# This is because it currently uses uv pip install on the requirements.txt file
# Does not have the same package management as using uv sync on the pyproject.toml
import sys
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, ".."))

DRAFT_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "draft_df.csv")

# -------------------------------------- Page content start ---------------------------------------
# Page configs
st.set_page_config(layout="wide")
st.markdown(f"<h3 style='text-align: center;'>Owner Profiles</h2>", unsafe_allow_html=True)

# Read data
draft_df = pd.read_csv(DRAFT_CSV_PATH)

# Select box
select_options_container = st.container()
select_options_cols = select_options_container.columns([1, 1, 1, 1])

# Custom CSS to make season selectbox a sticky header
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
select_options_cols[0].markdown("##### Owner")
selected_owner = select_options_cols[0].selectbox(label="Owner", options=owners_select_options, key="owners", label_visibility='collapsed')

# Select season to show
seasons = sorted(draft_df['Season'].unique(), reverse=True)
seasons_select_options = sorted(draft_df['Season'].astype(str).unique(), reverse=True)
seasons_select_options = [season[:4] + "-" + season[4:] for season in seasons_select_options]
seasons_select_options[0] = f"{seasons_select_options[0]} (Current)"
select_options_cols[1].markdown("##### Season")
selected_season_str = select_options_cols[1].selectbox(label="Season", options=seasons_select_options, key="seasons", label_visibility='collapsed')
selected_season_str = selected_season_str.replace("-", "")
if "Current" in selected_season_str:
    selected_season = seasons[seasons.index(int(selected_season_str.strip(" (Current)")))]
else:
    selected_season = seasons[seasons.index(int(selected_season_str))]