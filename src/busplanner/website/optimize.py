import streamlit as st
import pandas as pd

from busplanner.calculations.improver.main import optimise_schedule
from busplanner.website.upload import load_data


optimize_schedule = optimise_schedule


def optimize_display():
    st.header("3. Optimize the schedule")

    if "merged_schedule" not in st.session_state:
        st.warning(
            "Please upload and merge the distance matrix and timetable first."
        )
        st.stop()

    distance_matrix = st.session_state.get("distance_matrix")
    if distance_matrix is None and "distance_matrix_file" in st.session_state:
        try:
            distance_matrix = load_data(st.session_state["distance_matrix_file"])
            st.session_state["distance_matrix"] = distance_matrix
        except Exception:
            distance_matrix = None

    if distance_matrix is None:
        st.warning(
            "The distance matrix is missing. Please upload it again on the previous step."
        )
        st.stop()

    st.write(
        "The merged timetable and distance matrix can now be passed to the optimizer."
    )

    if st.button(
        "Run optimization",
        type="primary"
    ):
        start_soc = st.session_state.get("starting_energy", 100) / 100
        optimized_df = optimize_schedule(
            st.session_state["merged_schedule"],
            distance_matrix,
            start_soc=start_soc,
        )

        st.session_state["optimized_df"] = optimized_df

        st.success(
            "Optimization finished."
        )

        st.dataframe(
            optimized_df,
            use_container_width=True
        )
