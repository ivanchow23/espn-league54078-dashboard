# Install uv
curl -LsSf https://astral.sh/uv/0.9.9/install.sh | sh

# Add to path
source $HOME/.local/bin/env

# Clean-up existing venv
rm -r .venv

# Setup venv and install packages
# Use --frozen to not update lock file to set up consistent environments
uv sync --frozen

echo "Press any key to continue..."
read -n1 -s