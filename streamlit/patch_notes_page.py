import streamlit as st

patch_notes_list = [
"""
### v1.1.0
* Updated "Season to Display" selectbox to be "sticky" as user scrolls the page
* Minor updates to formatting
* Daily Points Stats:
  * Added "League Average" line to plot
  * Added "Smallest Gap" between ranks stat
  * Removed "League Average" stat
  * Fixed a bug where plot showed an extra day of data
* Points by Position Stats:
  * Updated layout to a table to condense more information
  * Added selectbox to show stats for last number of days
  * Added daily plots for each position
  * Added top players for each position
""",

"""
### v1.0.0
* Initial release
* Added the following stats:
  * Daily Points Stats
  * Points by Position Stats
  * Players with Different Owners Stats
  * Draft Stats
"""
]

# -------------------------------------- Page content start ---------------------------------------
st.set_page_config(layout="wide")
st.markdown(f"<h3 style='text-align: center;'>Patch Notes</h3>", unsafe_allow_html=True)

for patch_notes in patch_notes_list:
    st.markdown(patch_notes)