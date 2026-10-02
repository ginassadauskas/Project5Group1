import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Bus Schedule Optimizer PROTOTYPE 2",
    page_icon="🚌",
    layout="wide"
)

# =========================================================
# FUNCTIONS
# =========================================================

REQUIRED_COLUMNS = [
    "Bus",
    "Start",
    "End",
    "Start Time",
    "End Time"
]


def load_file(file):

    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)

    return pd.read_csv(file)


def validate_file(df):

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    return missing


def clean_data(df):

    report = []

    duplicates = df.duplicated().sum()

    if duplicates:
        df = df.drop_duplicates()

        report.append(
            f"Removed {duplicates} duplicate rows."
        )

    empty = df.isna().all(axis=1).sum()

    if empty:
        df = df.dropna(how="all")

        report.append(
            f"Removed {empty} empty rows."
        )

    missing = df.isna().sum().sum()

    if missing:
        df = df.ffill()

        report.append(
            f"Filled {missing} missing values."
        )

    if not report:
        report.append(
            "No cleaning problems were detected."
        )

    return df.reset_index(drop=True), report


def optimize(df):

    # Replace this with your optimization algorithm

    return df.copy()


# =========================================================
# HEADER
# =========================================================

st.title("🚌 Bus Schedule Optimizer")

st.caption(
    "Upload your schedule and improve its structure, "
    "quality and usability."
)

st.divider()


# =========================================================
# PROGRESS
# =========================================================

step = st.radio(
    "Process",
    [
        "① Upload",
        "② Check",
        "③ Clean",
        "④ Optimize",
        "⑤ Results"
    ],
    horizontal=True
)


# =========================================================
# STEP 1
# =========================================================

if step == "① Upload":

    st.header("Upload your bus schedule")

    st.write(
        "Upload an Excel or CSV file containing your "
        "bus schedule."
    )

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["xlsx", "csv"]
    )

    if uploaded_file:

        st.session_state["uploaded_file"] = uploaded_file

        st.success(
            f"Uploaded: {uploaded_file.name}"
        )

        df = load_file(uploaded_file)

        st.write("Preview:")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )


# =========================================================
# STEP 2
# =========================================================

elif step == "② Check":

    st.header("Check your schedule")

    if "uploaded_file" not in st.session_state:

        st.warning(
            "Please upload a file first."
        )

        st.stop()

    df = load_file(
        st.session_state["uploaded_file"]
    )

    missing = validate_file(df)

    if missing:

        st.error("Missing required columns:")

        for column in missing:
            st.write(f"❌ {column}")

    else:

        st.success(
            "✓ All required columns are present."
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Rows",
                len(df)
            )

        with col2:
            st.metric(
                "Columns",
                len(df.columns)
            )

        st.dataframe(
            df.head(20),
            use_container_width=True
        )


# =========================================================
# STEP 3
# =========================================================

elif step == "③ Clean":

    st.header("Clean the schedule")

    if "uploaded_file" not in st.session_state:
        st.warning("Please upload a file first.")
        st.stop()

    df = load_file(
        st.session_state["uploaded_file"]
    )

    cleaned_df, report = clean_data(df)

    st.subheader("Cleaning report")

    for item in report:

        st.success(
            "✓ " + item
        )

    st.subheader("Cleaned schedule")

    st.dataframe(
        cleaned_df,
        use_container_width=True
    )

    st.session_state["cleaned_df"] = cleaned_df


# =========================================================
# STEP 4
# =========================================================

elif step == "④ Optimize":

    st.header("Optimize the schedule")

    if "cleaned_df" not in st.session_state:

        st.warning(
            "Please complete the cleaning step first."
        )

        st.stop()

    st.write(
        "The optimization algorithm will now "
        "generate an improved bus schedule."
    )

    if st.button(
        "🚀 Run optimization",
        type="primary"
    ):

        optimized = optimize(
            st.session_state["cleaned_df"]
        )

        st.session_state["optimized_df"] = optimized

        st.success(
            "Optimization complete!"
        )

        st.dataframe(
            optimized,
            use_container_width=True
        )


# =========================================================
# STEP 5
# =========================================================

elif step == "⑤ Results":

    st.header("📊 Results")

    if "optimized_df" not in st.session_state:

        st.warning(
            "Please run the optimization first."
        )

        st.stop()

    df = st.session_state["optimized_df"]

    # Metrics

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total trips",
            len(df)
        )

    with col2:
        st.metric(
            "Buses",
            df["Bus"].nunique()
        )

    with col3:
        st.metric(
            "Schedule rows",
            len(df)
        )

    st.divider()

    # Graphs

    st.subheader("📈 Schedule graphs")

    if "Bus" in df.columns:

        trips_per_bus = (
            df["Bus"]
            .value_counts()
            .sort_index()
        )

        st.bar_chart(
            trips_per_bus
        )

    st.subheader("Optimized schedule")

    st.dataframe(
        df,
        use_container_width=True
    )

    # Download

    csv = df.to_csv(index=False)

    st.download_button(
        "⬇ Download schedule",
        csv,
        "optimized_bus_schedule.csv",
        "text/csv"
    )