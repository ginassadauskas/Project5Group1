import streamlit as st
import pandas as pd


def comparison_display():
    if "uploaded_file" not in st.session_state:
        st.warning(
            "Please upload a file first."
        )
        st.stop()

    df = load_data( # put in a real function to load the data from upload.py
        st.session_state["uploaded_file"]
    )

    cleaned_df, changes = clean_data(df) # put in a real function that cleans the data and returns the cleaned dataframe and a list of changes made

    st.subheader("Changes")

    for change in changes:
        st.success("✓ " + change)

    st.subheader("Cleaned schedule")

    st.dataframe(
        cleaned_df,
        use_container_width=True
    )

    st.session_state["cleaned_df"] = cleaned_df


comparison_display()

