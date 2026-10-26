import streamlit as st
import pandas as pd


def upload_display():
    st.header("1. Upload")

    upload_mode = st.radio(
        "Choose an upload option",
        [
            "Completed schedule",
            "Distance matrix + time table"
        ],
        horizontal=True,
        key="upload_mode"
    )

    if upload_mode == "Completed schedule":
        st.session_state.pop("distance_matrix_file", None)
        st.session_state.pop("time_table_file", None)

        st.write(
            "Please move on to the next step if you already have a completed bus schedule. Otherwise, you can upload the distance matrix and time table to build a new schedule."
        )

        uploaded_file = st.file_uploader(
            "Choose a completed schedule",
            type=["xlsx", "csv"],
            key="uploaded_schedule_file"
        )

        if uploaded_file is not None:
            st.session_state["uploaded_file"] = uploaded_file

            df = load_data(uploaded_file) # put in a real function to load the data

            st.success("Schedule uploaded successfully.")

            st.write("Preview")

            st.dataframe(
                df.head(20),
                use_container_width=True
            )
    else:
        st.session_state.pop("uploaded_file", None)

        st.write(
            "Upload both files needed to build the schedule: "
            "the distance matrix and the time table."
        )

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
            st.session_state["distance_matrix_file"] = distance_matrix_file
            st.session_state["time_table_file"] = time_table_file

            st.success("Both files uploaded successfully.")

            st.write("Distance matrix preview")
            st.dataframe(
                load_data(distance_matrix_file).head(20),
                use_container_width=True
            )

            st.write("Time table preview")
            st.dataframe(
                load_data(time_table_file).head(20), # put in a real function to load the data
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


upload_display()

