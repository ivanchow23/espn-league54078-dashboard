#!/bin/bash
# Download and re-generate data that includes the latest current season

echo "Running update_current_season_data.sh..."
cd $(dirname "$(realpath $0)")
echo "Changed working directory to $(pwd)"

# Configurations
source configs.sh
source .env

# Processing
echo "Updating current season ${CURRENT_SEASON} data..."

# Download latest season data
echo "Downloading data..."
uv run ../espn_league54078_fantasy_stats/espn_fantasy_api_scripts/espn_fantasy_api_downloader.py -l ${LEAGUE_ID} -s ${CURRENT_SEASON} -e ${CURRENT_SEASON} -o ${ESPN_FANTASY_API_DOWNLOADS_DIR} --espn_s2 "${ESPN_S2}"

# Re-generate data
./generate_data.sh