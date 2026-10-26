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
        "Results",
        "Comparison"
    ],
    horizontal=True
)


# ---------------------------------------------------------
# UPLOAD
# ---------------------------------------------------------

if step == "Upload":

    st.header("1. Upload")

    upload_mode = st.radio(
        "Choose an upload option",
        [
            "Completed schedule",
            "Distance matrix + time table"
        ],
        horizontal=True,
        key="upload_mode"
    )

    if upload_mode == "Completed schedule":

        st.session_state.pop("distance_matrix_file", None)
        st.session_state.pop("time_table_file", None)

        st.write(
            "Upload a single Excel or CSV file containing the "
            "completed bus schedule."
        )

        uploaded_file = st.file_uploader(
            "Choose a completed schedule",
            type=["xlsx", "csv"],
            key="uploaded_schedule_file"
        )

        if uploaded_file is not None:
            st.session_state["uploaded_file"] = uploaded_file

            df = load_data(uploaded_file)

            st.success("Schedule uploaded successfully.")

            st.write("Preview")

            st.dataframe(
                df.head(20),
                use_container_width=True
            )

    else:

        st.session_state.pop("uploaded_file", None)

        st.write(
            "Upload both files needed to build the schedule: "
            "the distance matrix and the time table."
        )

        distance_matrix_file = st.file_uploader(
            "Upload distance matrix",
            type=["xlsx", "csv"],
            key="distance_matrix_file"
        )

        time_table_file = st.file_uploader(
            "Upload time table",
            type=["xlsx", "csv"],
            key="time_table_file"
        )

        if distance_matrix_file is not None and time_table_file is not None:
            st.session_state["distance_matrix_file"] = distance_matrix_file
            st.session_state["time_table_file"] = time_table_file

            st.success("Both files uploaded successfully.")

            st.write("Distance matrix preview")
            st.dataframe(
                load_data(distance_matrix_file).head(20),
                use_container_width=True
            )

            st.write("Time table preview")
            st.dataframe(
                load_data(time_table_file).head(20),
                use_container_width=True
            )

        elif distance_matrix_file is not None or time_table_file is not None:
            st.info("Please upload both files to continue.")

    st.write("\n")
    starting_energy = st.slider(
        "Percentage of battery to start the buses",
        0,
        100,
        25
    )
    st.write(f"Input the starting energy for the buses: {starting_energy}%")


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


# ---------------------------------------------------------
# COMPARISON
# ---------------------------------------------------------

elif step == "Comparison":

    st.header("6. Compare before and after")

    if "cleaned_df" not in st.session_state:

        st.warning(
            "Please complete the cleaning step first."
        )

        st.stop()

    if "optimized_df" not in st.session_state:

        st.warning(
            "Please run the optimization first."
        )

        st.stop()

    before_df = st.session_state["cleaned_df"].copy()
    after_df = st.session_state["optimized_df"].copy()

    st.write(
        "Side-by-side view of the schedule before and after "
        "the optimization step."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Before optimization")
        st.dataframe(
            before_df,
            use_container_width=True,
            height=500
        )

    with col2:
        st.subheader("After optimization")
        st.dataframe(
            after_df,
            use_container_width=True,
            height=500
        )

