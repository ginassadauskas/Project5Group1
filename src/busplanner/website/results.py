import ast
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.patches import Patch

from busplanner.calculations.grade.kpi import trip_ratio


def _load_plot_gantt():
    gantt_path = Path(__file__).resolve().parents[1] / "calculations" / "improver" / "gantt.py"
    source = gantt_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(gantt_path))

    plot_func = next(
        (
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "plot_gantt"
        ),
        None,
    )

    if plot_func is None:
        raise ImportError("Could not find plot_gantt in gantt.py")

    namespace = {"plt": plt, "Patch": Patch}
    exec(compile(ast.Module(body=[plot_func], type_ignores=[]), str(gantt_path), "exec"), namespace, namespace)
    return namespace["plot_gantt"]


def results_display():
    st.header("5. Results")

    if "optimized_df" not in st.session_state:
        st.warning(
            "Please run the optimization first."
        )
        st.stop()

    df = st.session_state["optimized_df"]

    col1, col2, col3, col4, col5 = st.columns(5)

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

    with col5:
        st.metric(
            "Trip ratio",
            f"{trip_ratio(df):.2f}"
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

    required_columns = {"bus", "start time", "end time", "activity"}
    missing_columns = required_columns - set(df.columns)

    if not missing_columns:
        st.subheader("Gantt chart")
        plot_gantt = _load_plot_gantt()
        fig = plot_gantt(df)
        st.pyplot(fig)

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