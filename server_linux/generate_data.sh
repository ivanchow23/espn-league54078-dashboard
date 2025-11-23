#!/bin/bash
# Generate data from downloads

# Configurations
source configs.sh
espn_fantasy_api_downloads_dir=$(pwd)/espn_fantasy_api_downloads
output_dir="../docs/data"

# Generate data
echo "Generating data to ${output_dir}"
mkdir -p ${output_dir}
../espn_league54078_fantasy_stats/data_generator_scripts/data_generator_league_standings.py --out_dir_path ${output_dir}
../espn_league54078_fantasy_stats/data_generator_scripts/data_generator_draft.py --espn_fantasy_api_downloads_root_folder ${espn_fantasy_api_downloads_dir} --out_dir_path ${output_dir}
../espn_league54078_fantasy_stats/data_generator_scripts/data_generator_espn_fantasy_api_all_players_info.py --espn_fantasy_api_downloads_root_folder ${espn_fantasy_api_downloads_dir} --out_dir_path ${output_dir}
../espn_league54078_fantasy_stats/data_generator_scripts/data_generator_espn_fantasy_api_daily_rosters.py --espn_fantasy_api_downloads_root_folder ${espn_fantasy_api_downloads_dir} --out_dir_path ${output_dir}