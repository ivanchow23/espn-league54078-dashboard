import os
import importlib
import random
import pandas as pd
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
def get_daily_points(data_modified_time):
	return DailyPoints()


def format_season(season):
	season = str(season)
	return f'{season[:4]}-{season[4:]}'


def get_simulation_totals(daily_points, season, scoring_values):
	totals_df = daily_points.get_simulated_points_df(season, scoring_values, ACTUAL_SCORING_VALUES)
	position_totals_df = daily_points.get_simulated_points_by_position_df(
		season, scoring_values, ACTUAL_SCORING_VALUES
	)
	totals_df = totals_df.merge(position_totals_df, on='owner', how='left').fillna(0)
	first_place_points = totals_df['simulatedPoints'].iloc[0]
	totals_df['Difference from First'] = (totals_df['simulatedPoints'] - first_place_points).round(2)
	if first_place_points:
		percent_difference = (
			(totals_df['Difference from First'] / first_place_points) * 100
		).round(1)
	else:
		percent_difference = [0.0] * len(totals_df)
	totals_df['Percent Difference from First'] = percent_difference
	totals_df['simulatedPoints'] = totals_df['simulatedPoints'].round(2)
	totals_df.index = range(1, len(totals_df) + 1)
	return totals_df.rename(columns={'owner': 'Team Owner', 'simulatedPoints': 'Total Points'})[
		[
			'Team Owner', 'Total Points', 'Forwards', 'Defense', 'Goalies',
			'Difference from First', 'Percent Difference from First',
		]
	]


def reset_scoring_values():
	for stat, default in ACTUAL_SCORING_VALUES.items():
		st.session_state[f'scoring_{stat}'] = default


def optimize_scoring_values(daily_points, season, current_values, target_reduction_percent):
	season_df = daily_points._daily_rosters_df[
		(daily_points._daily_rosters_df['season'] == season)
		& ~daily_points._daily_rosters_df['lineupSlotId'].isin([7, 8])
	].copy()
	stat_totals = pd.DataFrame(index=season_df['owner'].unique())
	for stat, actual_value in ACTUAL_SCORING_VALUES.items():
		stat_totals[stat] = (
			pd.to_numeric(season_df[stat], errors='coerce').fillna(0)
			.div(actual_value)
			.groupby(season_df['owner'])
			.sum()
			.reindex(stat_totals.index, fill_value=0)
		)

	def get_spread(values):
		totals = stat_totals[list(values)] @ pd.Series(values)
		first = totals.max()
		last = totals.min()
		return last / first if first else 0.0

	target_spread = max(0.0, min(1.0, 1.0 - target_reduction_percent / 100.0))
	random_generator = random.Random()
	optimized_values = {
		stat: round(
			max(default * 0.25, min(default * 4.0, current_values[stat] * random_generator.uniform(0.75, 1.25))),
			2,
		)
		for stat, default in ACTUAL_SCORING_VALUES.items()
	}
	optimized_spread = get_spread(optimized_values)
	for _ in range(8):
		improved = False
		stat_order = list(ACTUAL_SCORING_VALUES)
		random_generator.shuffle(stat_order)
		for stat in stat_order:
			default = ACTUAL_SCORING_VALUES[stat]
			minimum = default * 0.25
			maximum = default * 4.0
			candidates = list({
				max(minimum, min(maximum, optimized_values[stat] * factor))
				for factor in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0)
			})
			random_generator.shuffle(candidates)
			best_value = optimized_values[stat]
			for candidate in candidates:
				candidate_values = dict(optimized_values, **{stat: candidate})
				candidate_spread = get_spread(candidate_values)
				if candidate_spread > optimized_spread:
					best_value = candidate
					optimized_spread = candidate_spread
					improved = True
			optimized_values[stat] = best_value
			if optimized_spread >= target_spread:
				break
		if optimized_spread >= target_spread or not improved:
			break

	for stat, value in optimized_values.items():
		st.session_state[f'scoring_{stat}'] = round(value, 2)
	st.session_state['optimization_message'] = (
		f'Optimized spread: {(optimized_spread - 1) * 100:.1f}% '
		f'({"within" if optimized_spread >= target_spread else "best found; target not reached"} '
		f'-{target_reduction_percent:.1f}%).'
	)


st.set_page_config(layout='wide')
st.markdown("<h3 style='text-align: center;'>Points Simulator</h2>", unsafe_allow_html=True)
st.caption('Adjust scoring values and compare the resulting totals using each season\'s rosters.')
st.caption('NOTE: This is experimental only and is basically vibe-coded with Copilot.')

daily_points_csv_path = daily_points_module.ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH
daily_points = get_daily_points(os.path.getmtime(daily_points_csv_path))
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

st.subheader('Optimize First - Last Place Spread')
st.caption('Auto-adjusts scoring values to reduce the spread between first and last place.')
st.session_state.setdefault('spread_reduction_percent', 5.0)
optimization_columns = st.columns([1, 1, 6], gap='small')
spread_reduction_percent = optimization_columns[0].number_input(
	'Reduce spread by (%)',
	min_value=0.0,
	max_value=100.0,
	step=0.5,
	format='%.1f',
	key='spread_reduction_percent',
	width='stretch',
)
optimization_columns[1].markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
st.markdown(
	'<style>.st-key-optimize-button button[kind="primary"] {background-color: #8bcf9b !important; border-color: #8bcf9b !important;}</style>',
	unsafe_allow_html=True,
)
with optimization_columns[1].container(key='optimize-button'):
	st.button(
		'Optimize',
		on_click=optimize_scoring_values,
		args=(daily_points, selected_season, scoring_values, spread_reduction_percent),
		width='stretch',
		type='primary',
	)
if 'optimization_message' in st.session_state:
	st.success(st.session_state['optimization_message'])

st.subheader(f'Team Totals')
totals = get_simulation_totals(daily_points, selected_season, scoring_values)
comparison_columns = ['Difference from First', 'Percent Difference from First']
st.dataframe(
	totals.style.applymap(
		lambda value: 'color: red' if value < 0 else '',
		subset=comparison_columns,
	).format({
		'Total Points': '{:.2f}',
		'Forwards': '{:.2f}',
		'Defense': '{:.2f}',
		'Goalies': '{:.2f}',
		'Difference from First': '{:.2f}',
		'Percent Difference from First': '{:.1f}%',
	}),
	use_container_width=True,
)

