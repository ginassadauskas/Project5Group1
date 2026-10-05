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
            f"Removed {duplicates} duplicate rows"
        )

    empty_rows = df.isna().all(axis=1).sum()

    if empty_rows:
        df = df.dropna(how="all")
        changes.append(
            f"Removed {empty_rows} empty rows"
        )

    missing = df.isna().sum().sum()

    if missing:
        df = df.ffill()
        changes.append(
            f"Filled {missing} missing values"
        )

    if not changes:
        changes.append("No problems were found")

    return df.reset_index(drop=True), changes


def optimize_schedule(df):
    # Replace this with the scheduling model
    return df.copy()


st.title("Bus Planning")

st.write(
    "Upload a bus schedule to check the data and create "
    "an improved schedule."
)

uploaded_file = st.file_uploader(
    "Choose a schedule",
    type=["xlsx", "csv"]
)


if uploaded_file:

    df = load_data(uploaded_file)

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        st.error("The following columns are missing:")

        for column in missing_columns:
            st.write(f"- {column}")

        st.stop()

    cleaned_df, changes = clean_data(df)
    optimized_df = optimize_schedule(cleaned_df)

    st.success("Schedule loaded successfully.")

    st.divider()

    st.subheader("Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Trips", len(optimized_df))

    with col2:
        st.metric(
            "Buses",
            optimized_df["bus"].nunique()
        )

    with col3:
        st.metric(
            "Locations",
            optimized_df["location"].nunique()
        )

    with col4:
        st.metric(
            "Activities",
            optimized_df["activity"].nunique()
        )

    st.divider()

    st.subheader("Schedule")

    st.dataframe(
        optimized_df,
        use_container_width=True
    )

    st.divider()

    st.subheader("Schedule overview")

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

    st.divider()

    st.subheader("Data cleaning")

    for change in changes:
        st.write("✓", change)

    st.divider()

    csv = optimized_df.to_csv(index=False)

    st.download_button(
        "Download schedule",
        csv,
        "optimized_schedule.csv",
        "text/csv"
    )