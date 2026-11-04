import ast
import io
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.patches import Patch

from busplanner.calculations.grade.kpi import kpi


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

    req_bus_line = st.session_state.get("merged_schedule")
    if req_bus_line is None:
        req_bus_line = st.session_state.get("bus_schedule")

    distance_matrix = st.session_state.get("distance_matrix")

    kpi_score = None
    if req_bus_line is not None and distance_matrix is not None:
        try:
            kpi_score = kpi(df, req_bus_line, distance_matrix)
        except Exception as exc:
            st.warning(f"KPI could not be calculated: {exc}")

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
        if kpi_score is None:
            st.metric("KPI score", "N/A")
        else:
            st.metric("KPI score", f"{kpi_score * 100:.2f}%")

    st.divider()

    if kpi_score is not None:
        st.subheader("KPI summary")
        st.write(f"Overall KPI score: {kpi_score:.4f} / 1.00")

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

    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    st.download_button(
        "Download optimized schedule",
        data=excel_buffer.getvalue(),
        file_name="optimized_schedule.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
