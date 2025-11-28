#!/bin/bash
# Initialize machine with all of the latest downloads needed

echo "Running initialize_downloads_cache.sh..."
cd $(dirname "$(realpath $0)")
echo "Changed working directory to $(pwd)"

# Configurations
source configs.sh
source .env

# Clear any existing downloads
echo "Removing and cleaning up ${ESPN_FANTASY_API_DOWNLOADS_DIR}..."
rm -r ${ESPN_FANTASY_API_DOWNLOADS_DIR}

# Download data
echo "Downloading data..."
uv run ../espn_league54078_fantasy_stats/espn_fantasy_api_scripts/espn_fantasy_api_downloader.py -l ${LEAGUE_ID} -s ${START_SEASON} -e ${CURRENT_SEASON} -o ${ESPN_FANTASY_API_DOWNLOADS_DIR} --espn_s2 "${ESPN_S2}"