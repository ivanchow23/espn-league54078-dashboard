#!/bin/bash
# Initialize machine with all of the latest downloads needed

# Configurations
source configs.sh
source .env
league_id=54078
espn_fantasy_api_downloads_dir=$(pwd)/espn_fantasy_api_downloads

# Clear any existing downloads
echo "Removing and cleaning up ${espn_fantasy_api_downloads_dir}..."
rm -r ${espn_fantasy_api_downloads_dir}

# Download data
echo "Downloading data..."
../espn_league54078_fantasy_stats/espn_fantasy_api_scripts/espn_fantasy_api_downloader.py -l ${league_id} -s ${START_SEASON} -e ${CURRENT_SEASON} -o ${espn_fantasy_api_downloads_dir} --espn_s2 "${ESPN_S2}"