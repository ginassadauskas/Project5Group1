from sqlalchemy import label
import streamlit as st
st.write("This is the profile page.")

st.file_uploader(
    "Upload File",
    type=None,
    accept=None,
    key="profile_upload",
    help="Upload a file for your profile.",
    on_change=None,
    args=None,
    kwargs=None,
    accept_multiple_files=False,
    disabled=False,
    label_visibility="visible",
)