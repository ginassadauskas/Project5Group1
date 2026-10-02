import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Bus Schedule Optimizer",
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

    elif file.name.endswith(".csv"):
        return pd.read_csv(file)


def clean_schedule(df):

    report = []

    original_rows = len(df)

    # Duplicate rows
    duplicates = df.duplicated().sum()

    df = df.drop_duplicates()

    if duplicates:
        report.append(
            f"{duplicates} duplicate rows removed"
        )

    # Empty rows
    empty_rows = df.isna().all(axis=1).sum()

    df = df.dropna(how="all")

    if empty_rows:
        report.append(
            f"{empty_rows} empty rows removed"
        )

    # Missing data
    missing = df.isna().sum().sum()

    if missing:

        df = df.ffill()

        report.append(
            f"{missing} missing values handled"
        )

    # Reset index
    df = df.reset_index(drop=True)

    if not report:

        report.append(
            "No cleaning problems detected"
        )

    return df, report


def optimize_schedule(df):

    # =====================================================
    # PUT YOUR ACTUAL OPTIMIZATION MODEL HERE
    # =====================================================

    optimized = df.copy()

    return optimized


# =========================================================
# TITLE
# =========================================================

st.title("🚌 Bus Schedule Optimizer")

st.write(
    """
    Upload a bus schedule to automatically check,
    clean and optimize the timetable.
    """
)

st.divider()


# =========================================================
# UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📁 Upload your bus schedule",
    type=["xlsx", "csv"]
)

if uploaded_file:

    original = load_file(uploaded_file)

    # =====================================================
    # VALIDATION
    # =====================================================

    missing_columns = [
        col
        for col in REQUIRED_COLUMNS
        if col not in original.columns
    ]

    if missing_columns:

        st.error(
            "Your file is missing required columns:"
        )

        st.write(missing_columns)

        st.stop()

    # =====================================================
    # PROCESS
    # =====================================================

    cleaned, report = clean_schedule(original)

    optimized = optimize_schedule(cleaned)

    # =====================================================
    # BEFORE / AFTER
    # =====================================================

    st.header("Before → After")

    before, after = st.columns(2)

    with before:

        st.subheader("📄 Original schedule")

        st.metric(
            "Rows",
            len(original)
        )

        st.dataframe(
            original.head(20),
            use_container_width=True
        )

    with after:

        st.subheader("✨ Optimized schedule")

        st.metric(
            "Rows",
            len(optimized)
        )

        st.dataframe(
            optimized.head(20),
            use_container_width=True
        )

    st.divider()

    # =====================================================
    # CLEANING REPORT
    # =====================================================

    st.header("🧹 What was changed?")

    for change in report:

        st.success(
            "✓ " + change
        )

    # =====================================================
    # STATISTICS
    # =====================================================

    st.header("📊 Schedule statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Original rows",
            len(original)
        )

    with col2:

        st.metric(
            "Final rows",
            len(optimized)
        )

    with col3:

        if "Bus" in optimized.columns:

            st.metric(
                "Buses",
                optimized["Bus"].nunique()
            )

    with col4:

        rows_removed = len(original) - len(optimized)

        st.metric(
            "Rows removed",
            rows_removed
        )

    # =====================================================
    # GRAPHS
    # =====================================================

    st.header("📈 Schedule visualization")

    col1, col2 = st.columns(2)

    with col1:

        if "Bus" in optimized.columns:

            st.subheader(
                "Trips per bus"
            )

            trips_per_bus = (
                optimized["Bus"]
                .value_counts()
                .sort_index()
            )

            st.bar_chart(
                trips_per_bus
            )

    with col2:

        if "Start" in optimized.columns:

            st.subheader(
                "Trips by starting location"
            )

            starts = (
                optimized["Start"]
                .value_counts()
                .head(10)
            )

            st.bar_chart(
                starts
            )

    # =====================================================
    # FULL RESULTS
    # =====================================================

    st.header("🚌 Final schedule")

    st.dataframe(
        optimized,
        use_container_width=True,
        height=500
    )

    # =====================================================
    # DOWNLOAD
    # =====================================================

    csv = optimized.to_csv(index=False)

    st.download_button(
        label="⬇ Download optimized schedule",
        data=csv,
        file_name="optimized_bus_schedule.csv",
        mime="text/csv",
        type="primary"
    )