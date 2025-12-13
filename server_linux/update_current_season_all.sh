#!/bin/bash
# Updates all current season related items
# Script downloads/re-generates current season data, commits data, pushes to remotes/origin, etc.
# Intended to be attached to a periodic cron job, or can be ran standalone.

echo "Running update_current_season_all.sh..."
cd $(dirname "$(realpath $0)")
echo "Changed working directory to $(pwd)"

# Configurations
source configs.sh
source .env

# Get datetime of when script started running
formatted_datetime=$(date +"%Y-%m-%d %H:%M:%S")

# Update current season data
./update_current_season_data.sh

# Push contents to GitHub Pages
git add ../docs
git commit -m "Update data ${formatted_datetime}" -m "Auto-generated commit with update_current_season_all.sh."
git push origin master