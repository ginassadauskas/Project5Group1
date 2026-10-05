import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="Bus Planning",
    page_icon="🚌",
    layout="wide"
)


required_columns = [
    "bus",
    "location",
    "activity",
    "start_time",
    "end_time"
]


def load_data(file):
    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)

    return pd.read_csv(file)


def clean_data(df):

    changes = []

    duplicates = df.duplicated().sum()

    if duplicates:
        df = df.drop_duplicates()
        changes.append(
            f"{duplicates} duplicate rows removed"
        )

    empty_rows = df.isna().all(axis=1).sum()

    if empty_rows:
        df = df.dropna(how="all")
        changes.append(
            f"{empty_rows} empty rows removed"
        )

    missing = df.isna().sum().sum()

    if missing:
        df = df.ffill()
        changes.append(
            f"{missing} missing values filled"
        )

    if not changes:
        changes.append(
            "No cleaning was required"
        )

    return df.reset_index(drop=True), changes


def optimize_schedule(df):
    # Replace this with your optimization model
    return df.copy()


st.title("Bus Planning")

st.write(
    "Compare the original schedule with the cleaned "
    "and optimized version."
)


uploaded_file = st.file_uploader(
    "Upload schedule",
    type=["xlsx", "csv"]
)


if uploaded_file:

    original = load_data(uploaded_file)

    missing = [
        column
        for column in required_columns
        if column not in original.columns
    ]

    if missing:

        st.error(
            "The uploaded file does not have all "
            "required columns."
        )

        st.write(missing)

        st.stop()

    cleaned, changes = clean_data(original)
    optimized = optimize_schedule(cleaned)

    st.success("Schedule processed.")

    # Before / after

    st.subheader("Original vs optimized")

    before, after = st.columns(2)

    with before:

        st.write("Original")

        st.metric(
            "Rows",
            len(original)
        )

        st.dataframe(
            original.head(15),
            use_container_width=True
        )

    with after:

        st.write("Optimized")

        st.metric(
            "Rows",
            len(optimized)
        )

        st.dataframe(
            optimized.head(15),
            use_container_width=True
        )

    st.divider()

    # Changes

    st.subheader("Changes made")

    for change in changes:
        st.write("✓", change)

    st.divider()

    # Overview

    st.subheader("Schedule overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Trips",
            len(optimized)
        )

    with col2:
        st.metric(
            "Buses",
            optimized["bus"].nunique()
        )

    with col3:
        st.metric(
            "Locations",
            optimized["location"].nunique()
        )

    with col4:
        st.metric(
            "Rows removed",
            len(original) - len(optimized)
        )

    st.divider()

    # Graphs

    st.subheader("Schedule analysis")

    graph1, graph2 = st.columns(2)

    with graph1:

        st.write("Activities")

        activity_counts = (
            optimized["activity"]
            .value_counts()
        )

        st.bar_chart(activity_counts)

    with graph2:

        st.write("Trips by location")

        location_counts = (
            optimized["location"]
            .value_counts()
        )

        st.bar_chart(location_counts)

    st.divider()

    # Final schedule

    st.subheader("Optimized schedule")

    st.dataframe(
        optimized,
        use_container_width=True,
        height=450
    )

    csv = optimized.to_csv(index=False)

    st.download_button(
        "Download optimized schedule",
        csv,
        "optimized_bus_schedule.csv",
        "text/csv"
    )