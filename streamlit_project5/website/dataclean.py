import streamlit as st
import pandas as pd


def clean_data_display():
    st.header("3. Clean the data")

    if "uploaded_file" not in st.session_state:
        st.warning(
            "Please upload a file first."
        )
        st.stop()

    df = load_data(
        st.session_state["uploaded_file"]
    )

    cleaned_df, changes = clean_data(df)

    st.subheader("Changes")

    for change in changes:
        st.success("✓ " + change)

    st.subheader("Cleaned schedule")

    st.dataframe(
        cleaned_df,
        use_container_width=True
    )

    st.session_state["cleaned_df"] = cleaned_df


clean_data_display()