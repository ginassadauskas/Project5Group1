import streamlit as st
import pandas as pd

from busplanner.calculations.imports import normalize_dataframe_columns
from busplanner.calculations.main import merged


def load_data(uploaded_file):
    """Load a CSV or Excel file into a pandas DataFrame."""
    file_name = str(uploaded_file.name).lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if file_name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)

    raise ValueError(f"Unsupported file type: {uploaded_file.name}")


def upload_display():
    st.header("1. Upload")

    st.write(
        "Upload the distance matrix and the timetable to build the schedule."
    )

    # Keep file uploader values in local variables; do not overwrite the widget-managed
    # keys in st.session_state with the same names.
    distance_matrix_file = st.file_uploader(
        "Upload distance matrix",
        type=["xlsx", "csv"],
        key="distance_matrix_file"
    )

    time_table_file = st.file_uploader(
        "Upload time table",
        type=["xlsx", "csv"],
        key="time_table_file"
    )

    if distance_matrix_file is not None and time_table_file is not None:
        distance_matrix = normalize_dataframe_columns(load_data(distance_matrix_file))
        time_table = normalize_dataframe_columns(load_data(time_table_file))

        st.session_state["distance_matrix"] = distance_matrix
        st.session_state["time_table"] = time_table

        merged_schedule = merged(time_table, distance_matrix)

        st.session_state["merged_schedule"] = merged_schedule

        st.success("Both files uploaded successfully and merged.")

        st.write("Distance matrix preview")
        st.dataframe(
            distance_matrix.head(20),
            use_container_width=True
        )

        st.write("Time table preview")
        st.dataframe(
            time_table.head(20),
            use_container_width=True
        )

        st.write("Merged preview")
        st.dataframe(
            merged_schedule,
            use_container_width=True
        )
    elif distance_matrix_file is not None or time_table_file is not None:
        st.info("Please upload both files to continue.")

    st.write("\n")
    starting_energy = st.slider(
        "Percentage of battery to start the buses",
        0,
        100,
        25
    )
    st.write(f"Input the starting energy for the buses: {starting_energy}%")


