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


def check_data(df):
    missing = []

    for column in required_columns:
        if column not in df.columns:
            missing.append(column)

    return missing


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
        changes.append(
            "No cleaning was necessary"
        )

    return df.reset_index(drop=True), changes


def optimize_schedule(df):
    # Add the actual optimization model here.
    return df.copy()


st.title("Bus Schedule Optimizer")

st.write(
    "Upload a schedule and go through the different "
    "steps to create an improved timetable."
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


# ---------------------------------------------------------
# UPLOAD
# ---------------------------------------------------------

if step == "Upload":

    st.header("1. Upload")

    st.write(
        "Upload an Excel or CSV file containing the "
        "bus schedule."
    )

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["xlsx", "csv"]
    )

    if uploaded_file is not None:

        st.session_state["uploaded_file"] = uploaded_file

        df = load_data(uploaded_file)

        st.success("File uploaded successfully.")

        st.write("Preview")

        st.dataframe(
            df.head(20),
            use_container_width=True
        )


# ---------------------------------------------------------
# CHECK
# ---------------------------------------------------------

elif step == "Check":

    st.header("2. Check the data")

    if "uploaded_file" not in st.session_state:

        st.warning(
            "Please upload a file first."
        )

        st.stop()

    df = load_data(
        st.session_state["uploaded_file"]
    )

    missing = check_data(df)

    if missing:

        st.error(
            "The following columns are missing:"
        )

        for column in missing:
            st.write(f"- {column}")

    else:

        st.success(
            "All required columns are present."
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Rows",
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

        st.dataframe(
            df.head(20),
            use_container_width=True
        )


# ---------------------------------------------------------
# CLEAN
# ---------------------------------------------------------

elif step == "Clean":

    st.header("3. Clean the data")

    if "uploaded_file" not in st.session_state:

        st.warning(
            "Please upload a file first."
        )

        st.stop()

    df = load_data(
        st.session_state["uploaded_file"]
    )

    cleaned_df, changes = clean_data(df)

    st.subheader("Changes")

    for change in changes:
        st.success("✓ " + change)

    st.subheader("Cleaned schedule")

    st.dataframe(
        cleaned_df,
        use_container_width=True
    )

    st.session_state["cleaned_df"] = cleaned_df


# ---------------------------------------------------------
# OPTIMIZE
# ---------------------------------------------------------

elif step == "Optimize":

    st.header("4. Optimize the schedule")

    if "cleaned_df" not in st.session_state:

        st.warning(
            "Please complete the cleaning step first."
        )

        st.stop()

    st.write(
        "The cleaned schedule can now be passed to "
        "the optimization model."
    )

    if st.button(
        "Run optimization",
        type="primary"
    ):

        optimized_df = optimize_schedule(
            st.session_state["cleaned_df"]
        )

        st.session_state["optimized_df"] = optimized_df

        st.success(
            "Optimization finished."
        )

        st.dataframe(
            optimized_df,
            use_container_width=True
        )


# ---------------------------------------------------------
# RESULTS
# ---------------------------------------------------------

elif step == "Results":

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