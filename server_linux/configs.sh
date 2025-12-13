# configs.sh
# Store variables and other configurations to be used by other scripts

# League information
# Seasons represent "end year" of the given season
# Example: 2015 represents the 20142015 season
START_SEASON=2015
CURRENT_SEASON=2026
LEAGUE_ID=54078

# Input and output data directories
CONFIGS_SH_DIR=$(dirname "$(realpath $0)")
ESPN_FANTASY_API_DOWNLOADS_DIR=${CONFIGS_SH_DIR}/espn_fantasy_api_downloads
DATA_GEN_OUTPUT_DIR=${CONFIGS_SH_DIR}/../docs/data