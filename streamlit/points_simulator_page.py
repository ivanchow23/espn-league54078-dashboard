import os
import importlib
import streamlit as st

# Workaround for import stats to deploy on streamlit app
# This is because it currently uses uv pip install on the requirements.txt file
# Does not have the same package management as using uv sync on the pyproject.toml
import sys
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, ".."))

import stats.daily_points as daily_points_module
daily_points_module = importlib.reload(daily_points_module)
DailyPoints = daily_points_module.DailyPoints


ACTUAL_SCORING_VALUES = {
	'BLK': 0.5,
	'GWG': 1.0,
	'PPP': 1.0,
	'SHP': 1.0,
	'G': 3.0,
	'A': 3.0,
	'W': 6.0,
	'SV': 0.03,
	'SO': 3.0,
	'OTL': 3.0,
	'HAT': 6.0,
}
EARLIEST_SUPPORTED_SEASON = 20232024


@st.cache_resource
def get_daily_points():
	return DailyPoints()


def format_season(season):
	season = str(season)
	return f'{season[:4]}-{season[4:]}'


def get_simulation_totals(daily_points, season, scoring_values):
	totals_df = daily_points.get_simulated_points_df(season, scoring_values, ACTUAL_SCORING_VALUES)
	first_place_points = totals_df['simulatedPoints'].iloc[0]
	totals_df['Difference from First'] = (totals_df['simulatedPoints'] - first_place_points).round(2)
	if first_place_points:
		totals_df['Percent Difference from First'] = (
			(totals_df['Difference from First'] / first_place_points) * 100
		).round(1)
	else:
		totals_df['Percent Difference from First'] = 0.0
	totals_df['simulatedPoints'] = totals_df['simulatedPoints'].round(2)
	totals_df.index = range(1, len(totals_df) + 1)
	return totals_df.rename(columns={'owner': 'Team Owner', 'simulatedPoints': 'Total Points'})[
		['Team Owner', 'Total Points', 'Difference from First', 'Percent Difference from First']
	]


def reset_scoring_values():
	for stat, default in ACTUAL_SCORING_VALUES.items():
		st.session_state[f'scoring_{stat}'] = default


st.set_page_config(layout='wide')
st.markdown("<h3 style='text-align: center;'>Points Simulator</h2>", unsafe_allow_html=True)
st.caption('Adjust scoring values and compare the resulting totals using each season\'s rosters.')
st.caption('NOTE: This is experimental only and is basically vibe-coded with Copilot.')

daily_points = get_daily_points()
seasons = [season for season in daily_points.get_seasons() if int(season) >= EARLIEST_SUPPORTED_SEASON]
season_labels = {format_season(season): season for season in seasons}
season_select_container = st.container()
season_select_container.markdown('#### Season')
season_select_cols = season_select_container.columns([1, 3])
selected_season_label = season_select_cols[0].selectbox(
	label='Show Season',
	options=list(reversed(season_labels)),
	label_visibility='collapsed',
)
selected_season = season_labels[selected_season_label]

st.subheader('Scoring Values')
st.markdown(
	"""
<style>
div[data-testid="stVerticalBlock"]:has(div.reset-scoring-button) button[kind="primary"] {
	background-color: #c75b5b;
	border-color: #c75b5b;
    color: white;
}
div[data-testid="stVerticalBlock"]:has(div.reset-scoring-button) button[kind="primary"]:hover {
	background-color: #ad4f4f;
	border-color: #ad4f4f;
    color: white;
}
</style>
<div class="reset-scoring-button"></div>
""",
	unsafe_allow_html=True,
)
st.button('Reset to Defaults', on_click=reset_scoring_values, type='primary')
scoring_columns = st.columns(6, gap='small')
scoring_values = {}
for index, (stat, default) in enumerate(ACTUAL_SCORING_VALUES.items()):
	st.session_state.setdefault(f'scoring_{stat}', default)
	scoring_values[stat] = scoring_columns[index % 6].number_input(
		stat,
		min_value=0.0,
		step=0.01,
		format='%.2f',
		key=f'scoring_{stat}',
		width='stretch',
	)

st.subheader(f'Team Totals')
totals = get_simulation_totals(daily_points, selected_season, scoring_values)
comparison_columns = ['Difference from First', 'Percent Difference from First']
st.dataframe(
	totals.style.applymap(
		lambda value: 'color: red' if value < 0 else '',
		subset=comparison_columns,
	).format({
		'Total Points': '{:.2f}',
		'Difference from First': '{:.2f}',
		'Percent Difference from First': '{:.1f}',
	}),
	use_container_width=True,
)

