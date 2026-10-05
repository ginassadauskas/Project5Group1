import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="Bus Schedule Optimizer",
    page_icon="🚌",
    layout="wide"
)


required_columns = [
    "bus",
    "start location",
    "activity",
    "start time",
    "end time",
    "end location"
]


def load_data(file):
    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)

    return pd.read_csv(file)


def clean_data(df):
    changes = []

    duplicates = df.duplicated().sum()

    if duplicates > 0:
        df = df.drop_duplicates()
        changes.append(
            f"Removed {duplicates} duplicate rows"
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

    if not changes:
        changes.append("No cleaning was necessary")

    return df.reset_index(drop=True), changes


def optimize_schedule(df):
    # The actual optimization model can be added here.
    return df.copy()


st.title("Bus Schedule Optimizer")

st.write(
    "Upload a bus schedule to check, clean and improve the data."
)

st.divider()


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

        st.error("The following required columns are missing:")

        for column in missing_columns:
            st.write(f"- {column}")

        st.stop()

    st.success("File uploaded successfully.")

    cleaned_df, changes = clean_data(df)

    optimized_df = optimize_schedule(cleaned_df)

    st.divider()

    st.subheader("Schedule overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Trips",
            len(optimized_df)
        )

    with col2:
        st.metric(
            "Buses",
            optimized_df["bus"].nunique()
        )

    with col3:
        st.metric(
            "Start locations",
            optimized_df["start location"].nunique()
        )

    with col4:
        st.metric(
            "End locations",
            optimized_df["end location"].nunique()
        )

    st.divider()

    st.subheader("Optimized schedule")

    st.dataframe(
        optimized_df,
        use_container_width=True,
        height=400
    )

    st.divider()

    st.subheader("Schedule analysis")

    left, right = st.columns(2)

    with left:

        st.write("Activities")

        activity_counts = (
            optimized_df["activity"]
            .value_counts()
        )

        st.bar_chart(activity_counts)

    with right:

        st.write("Trips per bus")

        bus_counts = (
            optimized_df["bus"]
            .value_counts()
            .sort_index()
        )

        st.bar_chart(bus_counts)

    left, right = st.columns(2)

    with left:

        st.write("Starting locations")

        start_locations = (
            optimized_df["start location"]
            .value_counts()
        )

        st.bar_chart(start_locations)

    with right:

        st.write("Ending locations")

        end_locations = (
            optimized_df["end location"]
            .value_counts()
        )

        st.bar_chart(end_locations)

    st.divider()

    st.subheader("Data cleaning")

    for change in changes:
        st.write("✓", change)

    st.divider()

    csv_file = optimized_df.to_csv(index=False)

    st.download_button(
        "Download optimized schedule",
        data=csv_file,
        file_name="optimized_schedule.csv",
        mime="text/csv"
    )