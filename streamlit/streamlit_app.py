import streamlit as st

VERSION = "v1.1.0"

# Define the pages
current_season_page = st.Page("current_season_page.py", title="Current Season")
patch_notes_page = st.Page("patch_notes_page.py", title="Patch Notes")

# Set up navigation
pg = st.navigation([current_season_page, patch_notes_page])

# Version info on sidebar
with st.sidebar:
    st.markdown(f"Version: {VERSION}")

# Run the selected page
pg.run()