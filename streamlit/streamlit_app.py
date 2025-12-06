import streamlit as st

# Define the pages
current_season_page = st.Page("current_season_page.py", title="Current Season")
# Set up navigation
pg = st.navigation([current_season_page])

# Run the selected page
pg.run()