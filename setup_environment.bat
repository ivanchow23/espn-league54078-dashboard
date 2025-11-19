:: Install uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/0.9.9/install.ps1 | iex"

:: Clean-up existing venv
rmdir /s /q .venv

:: Setup venv and install packages
:: Use --frozen to not update lock file to set up consistent environments
uv sync --frozen

pause