import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="Bus Schedule Optimizer",
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


def check_data(df):
    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    return missing


def clean_data(df):
    changes = []

    duplicate_count = df.duplicated().sum()

    if duplicate_count:
        df = df.drop_duplicates()

        changes.append(
            f"{duplicate_count} duplicate rows removed"
        )

    empty_count = df.isna().all(axis=1).sum()

    if empty_count:
        df = df.dropna(how="all")

        changes.append(
            f"{empty_count} empty rows removed"
        )

    missing_count = df.isna().sum().sum()

    if missing_count:
        df = df.ffill()

        changes.append(
            f"{missing_count} missing values filled"
        )

    if not changes:
        changes.append("No cleaning was necessary")

    return df.reset_index(drop=True), changes


def optimize_schedule(df):
    # Add the actual optimization model here
    return df.copy()


st.title("Bus Schedule Optimizer")

st.write(
    "A tool for cleaning and improving bus schedules."
)

st.divider()


step = st.radio(
    "Step",
    [
        "Upload",
        "Check",
        "Clean",
        "Optimize",
        "Results"
    ],
    horizontal=True
)


if step == "Upload":

    st.header("Upload")

    st.write(
        "Choose the Excel or CSV file containing the "
        "bus schedule."
    )

    file = st.file_uploader(
        "Schedule file",
        type=["xlsx", "csv"]
    )

    if file:
        st.session_state["file"] = file

        df = load_data(file)

        st.success("File uploaded.")

        st.write("Preview")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )


elif step == "Check":

    st.header("Check the data")

    if "file" not in st.session_state:
        st.warning("Upload a file first.")
        st.stop()

    df = load_data(
        st.session_state["file"]
    )

    missing = check_data(df)

    if missing:

        st.error("Some columns are missing.")

        for column in missing:
            st.write(f"- {column}")

    else:

        st.success(
            "All required columns were found."
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Rows", len(df))

        with col2:
            st.metric("Buses", df["bus"].nunique())

        with col3:
            st.metric(
                "Locations",
                df["location"].nunique()
            )

        st.dataframe(
            df.head(20),
            use_container_width=True
        )


elif step == "Clean":

    st.header("Clean the data")

    if "file" not in st.session_state:
        st.warning("Upload a file first.")
        st.stop()

    df = load_data(
        st.session_state["file"]
    )

    cleaned_df, changes = clean_data(df)

    for change in changes:
        st.success("✓ " + change)

    st.write("Cleaned schedule")

    st.dataframe(
        cleaned_df,
        use_container_width=True
    )

    st.session_state["cleaned"] = cleaned_df


elif step == "Optimize":

    st.header("Optimize the schedule")

    if "cleaned" not in st.session_state:
        st.warning("Clean the data first.")
        st.stop()

    st.write(
        "The cleaned schedule can now be passed to "
        "the optimization model."
    )

    if st.button(
        "Run optimization",
        type="primary"
    ):

        result = optimize_schedule(
            st.session_state["cleaned"]
        )

        st.session_state["optimized"] = result

        st.success(
            "Optimization finished."
        )

        st.dataframe(
            result,
            use_container_width=True
        )


elif step == "Results":

    st.header("Results")

    if "optimized" not in st.session_state:
        st.warning("Run the optimization first.")
        st.stop()

    df = st.session_state["optimized"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Trips", len(df))

    with col2:
        st.metric("Buses", df["bus"].nunique())

    with col3:
        st.metric(
            "Locations",
            df["location"].nunique()
        )

    st.divider()

    st.subheader("Activities")

    activities = df["activity"].value_counts()

    st.bar_chart(activities)

    st.subheader("Schedule")

    st.dataframe(
        df,
        use_container_width=True
    )

    csv = df.to_csv(index=False)

    st.download_button(
        "Download optimized schedule",
        csv,
        "optimized_schedule.csv",
        "text/csv"
    )