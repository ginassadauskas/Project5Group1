import streamlit as st
import pandas as pd


def results_display():
    st.header("5. Results")

    if "optimized_df" not in st.session_state:
        st.warning(
            "Please run the optimization first."
        )
        st.stop()

    df = st.session_state["optimized_df"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Trips",
            len(df)
        )

    with col2:
        st.metric(
            "Buses",
            df["bus"].nunique()
        )

    with col3:
        st.metric(
            "Start locations",
            df["start location"].nunique()
        )

    with col4:
        st.metric(
            "End locations",
            df["end location"].nunique()
        )

    st.divider()

    st.subheader("Activities")

    activity_counts = (
        df["activity"]
        .value_counts()
    )

    st.bar_chart(activity_counts)

    st.subheader("Trips per bus")

    bus_counts = (
        df["bus"]
        .value_counts()
        .sort_index()
    )

    st.bar_chart(bus_counts)

    st.subheader("Optimized schedule")

    st.dataframe(
        df,
        use_container_width=True,
        height=450
    )

    csv_file = df.to_csv(index=False)

    st.download_button(
        "Download optimized schedule",
        data=csv_file,
        file_name="optimized_schedule.csv",
        mime="text/csv"
    )


results_display()