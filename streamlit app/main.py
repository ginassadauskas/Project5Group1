import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="Bus Schedule Optimizer PROTOTYPE 1",
    page_icon="🚌",
    layout="wide"
)


required_columns = [
    "Bus",
    "Start",
    "End",
    "Start Time",
    "End Time"
]


def load_data(file):
    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    elif file.name.endswith(".csv"):
        return pd.read_csv(file)


def clean_data(df):
    changes = []

    duplicate_rows = df.duplicated().sum()

    if duplicate_rows > 0:
        df = df.drop_duplicates()
        changes.append(
            f"Removed {duplicate_rows} duplicate rows"
        )

    empty_rows = df.isna().all(axis=1).sum()

    if empty_rows > 0:
        df = df.dropna(how="all")
        changes.append(
            f"Removed {empty_rows} empty rows"
        )

    missing_values = df.isna().sum().sum()

    if missing_values > 0:
        df = df.ffill()
        changes.append(
            f"Filled {missing_values} missing values"
        )

    if len(changes) == 0:
        changes.append("No cleaning was necessary")

    return df.reset_index(drop=True), changes


def optimize_schedule(df):
    # Add the scheduling algorithm here
    optimized = df.copy()

    return optimized


st.title("Bus Schedule Optimizer")

st.write(
    "Upload a bus schedule to check, clean and optimize the data."
)

uploaded_file = st.file_uploader(
    "Upload an Excel or CSV file",
    type=["xlsx", "csv"]
)


if uploaded_file is not None:

    df = load_data(uploaded_file)

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        st.error("Some required columns are missing:")

        for column in missing_columns:
            st.write(f"- {column}")

        st.stop()

    st.success("File uploaded successfully.")

    st.subheader("Original schedule")

    st.dataframe(
        df,
        use_container_width=True
    )

    cleaned_df, changes = clean_data(df)

    optimized_df = optimize_schedule(cleaned_df)

    st.divider()

    st.subheader("What was changed?")

    for change in changes:
        st.write("✓", change)

    st.divider()

    st.subheader("Schedule overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Original rows",
            len(df)
        )

    with col2:
        st.metric(
            "Final rows",
            len(optimized_df)
        )

    with col3:
        if "Bus" in optimized_df.columns:
            st.metric(
                "Number of buses",
                optimized_df["Bus"].nunique()
            )

    st.divider()

    st.subheader("Before and after")

    before, after = st.columns(2)

    with before:
        st.write("Original")
        st.dataframe(
            df.head(20),
            use_container_width=True
        )

    with after:
        st.write("Optimized")
        st.dataframe(
            optimized_df.head(20),
            use_container_width=True
        )

    st.divider()

    st.subheader("Graphs")

    graph1, graph2 = st.columns(2)

    with graph1:

        if "Bus" in optimized_df.columns:

            st.write("Number of trips per bus")

            trips_per_bus = (
                optimized_df["Bus"]
                .value_counts()
                .sort_index()
            )

            st.bar_chart(trips_per_bus)

    with graph2:

        if "Start" in optimized_df.columns:

            st.write("Trips by starting location")

            starts = (
                optimized_df["Start"]
                .value_counts()
                .head(10)
            )

            st.bar_chart(starts)

    st.divider()

    st.subheader("Optimized schedule")

    st.dataframe(
        optimized_df,
        use_container_width=True
    )

    csv_file = optimized_df.to_csv(index=False)

    st.download_button(
        "Download optimized schedule",
        data=csv_file,
        file_name="optimized_bus_schedule.csv",
        mime="text/csv"
    )