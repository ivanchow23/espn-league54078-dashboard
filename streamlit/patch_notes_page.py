import streamlit as st

patch_notes_list = [
""" ### v1.0.0
* Initial release
* Added the following stats:
  * Daily points graph
  * Players with different owners
  * Draft stats per owner
"""
]

# -------------------------------------- Page content start ---------------------------------------
st.set_page_config(layout="wide")
st.markdown(f"<h3 style='text-align: center;'>Patch Notes</h3>", unsafe_allow_html=True)

for patch_notes in patch_notes_list:
    st.markdown(patch_notes)