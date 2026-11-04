import pandas as pd
import streamlit as st


def comparison_display():
    """Show the original uploaded bus schedule next to the optimized schedule."""
    st.header("6. Compare schedules")

    original_df = st.session_state.get("bus_schedule")
    optimized_df = st.session_state.get("optimized_df")

    if original_df is None:
        st.warning(
            "Please upload and validate a bus schedule first."
        )
        st.stop()

    if optimized_df is None:
        st.warning(
            "Please run the optimization first before comparing schedules."
        )
        st.stop()

    original_df = pd.DataFrame(original_df)
    optimized_df = pd.DataFrame(optimized_df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Original rows", len(original_df))

    with col2:
        st.metric("Optimized rows", len(optimized_df))

    with col3:
        original_buses = original_df["bus"].nunique() if "bus" in original_df.columns else 0
        st.metric("Original buses", original_buses)

    with col4:
        optimized_buses = optimized_df["bus"].nunique() if "bus" in optimized_df.columns else 0
        st.metric("Optimized buses", optimized_buses)

    st.divider()

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Original bus schedule")
        st.dataframe(original_df, use_container_width=True)

    with right_col:
        st.subheader("Optimized bus schedule")
        st.dataframe(optimized_df, use_container_width=True)

    st.subheader("Changes summary")
    st.write(
        "This comparison uses the validated original schedule stored in the check step "
        "and the optimized schedule produced in the optimization step."
    )

