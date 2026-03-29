import streamlit as st

VERSION = "v1.1.0"

# Define the pages
season_dashboard_page = st.Page("season_dashboard_page.py", title="Season Dashboard")
patch_notes_page = st.Page("patch_notes_page.py", title="Patch Notes")

# Set up navigation
pg = st.navigation([season_dashboard_page, patch_notes_page])

# Version info on sidebar
with st.sidebar:
    st.markdown(f"Version: {VERSION}")

# Run the selected page
pg.run()