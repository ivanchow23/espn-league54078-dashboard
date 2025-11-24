#!/bin/bash
# Generate data from downloads

# Configurations
source configs.sh

# Generate data
echo "Generating data to ${DATA_GEN_OUTPUT_DIR}"
mkdir -p ${DATA_GEN_OUTPUT_DIR}
uv run ../espn_league54078_fantasy_stats/data_generator_scripts/data_generator_league_standings.py --out_dir_path ${DATA_GEN_OUTPUT_DIR}
uv run ../espn_league54078_fantasy_stats/data_generator_scripts/data_generator_draft.py --espn_fantasy_api_downloads_root_folder ${ESPN_FANTASY_API_DOWNLOADS_DIR} --out_dir_path ${DATA_GEN_OUTPUT_DIR}
uv run ../espn_league54078_fantasy_stats/data_generator_scripts/data_generator_espn_fantasy_api_all_players_info.py --espn_fantasy_api_downloads_root_folder ${ESPN_FANTASY_API_DOWNLOADS_DIR} --out_dir_path ${DATA_GEN_OUTPUT_DIR}
uv run ../espn_league54078_fantasy_stats/data_generator_scripts/data_generator_espn_fantasy_api_daily_rosters.py --espn_fantasy_api_downloads_root_folder ${ESPN_FANTASY_API_DOWNLOADS_DIR} --out_dir_path ${DATA_GEN_OUTPUT_DIR}