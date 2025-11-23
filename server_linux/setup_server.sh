#!/bin/bash

# Prompt user for espn_s2 cookie if not already stored
# This will be stored in a file locally but be .gitignore'ed
echo "Setting up environment variables..."
env_file=".env"
if [ -e "$env_file" ]; then
  echo "Environment variables already stored."
else
    echo "Enter espn_s2 cookie string for downloading ESPN fantasy API data. This can be found by:"
    echo " - Logging into https://www.espn.com/fantasy"
    echo " - Pressing F12 to inspect elements"
    echo " - Looking for the "espn_s2" cookie."

    read -p "Enter string: " espn_s2
    echo "Writing to .env"
    echo "ESPN_S2=$espn_s2" > .env
fi

# Download required data to machine
./initialize_downloads_cache.sh

# Generate data
./generate_data.sh