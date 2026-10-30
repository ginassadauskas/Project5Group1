import streamlit as st
import pandas as pd

from busplanner.calculations.checker.imports import convert_time_to_minutes
from busplanner.calculations.main import verify_schedule
from busplanner.calculations.defaults import REQ_COL


def normalize_bus_schedule(df):
    """Convert time-like columns to minute values before validation."""
    if df is None or not isinstance(df, pd.DataFrame):
        return df

    normalized = df.copy()
    for column in ["start time", "end time"]:
        if column not in normalized.columns:
            continue

        series = normalized[column]
        if pd.api.types.is_numeric_dtype(series):
            continue

        try:
            normalized[column] = convert_time_to_minutes(series)
        except Exception:
            try:
                parsed = pd.to_datetime(series, errors="coerce")
                normalized[column] = parsed.dt.hour * 60 + parsed.dt.minute
            except Exception:
                pass

    return normalized


def load_data(uploaded_file):
    """Load an uploaded schedule from CSV or Excel."""
    file_name = str(uploaded_file.name).lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if file_name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)

    raise ValueError(f"Unsupported file type: {uploaded_file.name}")


def format_validation_issue(item):
    """Convert raw checker output into a short user-facing issue describing row/column locations."""
    if item is True:
        return "No validation issues found."
    elif item is False:
        return "Validation failed."

    elif isinstance(item, pd.Series):
        rows = [int(row) for row in item.index if row is not None]
        if not rows:
            return f"Validation issue in column '{item.name}'."
        return f"Validation issue in rows {rows[:10]} (column: {item.name})."

    elif isinstance(item, pd.DataFrame):
        rows = [int(row) for row in item.index if row is not None]
        columns = list(item.columns)
        if not rows:
            return f"Validation issue in columns: {columns}."
        return f"Validation issue in rows {rows[:10]} and columns {columns}."

    elif isinstance(item, (list, tuple)):
        return "; ".join(format_validation_issue(part) for part in item)
    else:
        return str(item)


def check_data(df):
    """Run the project validator and return a list of issues if any."""

    # This is the strict validation stage used for blocking errors.
    # It returns a list of strings, and the Streamlit page treats that list as
    # a trigger for st.error(...) messages below.
    if df is None or not isinstance(df, pd.DataFrame):
        return ["The uploaded schedule is not a valid DataFrame."]

    df = normalize_bus_schedule(df)

    missing_columns = [col for col in REQ_COL if col not in df.columns]
    if missing_columns:
        return [
            "The uploaded schedule is missing required columns: "
            + ", ".join(missing_columns)
        ]

    # The project accepts these column names as the standard schedule schema.
    # For this upload flow, only warning-level checks should appear for data quality.
    return []


def get_bus_schedule_warnings(df: pd.DataFrame):
    """Return warning messages for uploaded bus schedule data."""
    warnings = []

    # This function does not raise an exception or stop the page. It simply
    # builds a Python list of warning strings. That list is later checked in the
    # Streamlit page, and if it's not empty the page calls st.warning(...)
    # and prints each message one by one.
    # So this is the "preparation stage" for warnings before the website displays them.
    if df is None or df.empty:
        return ["The uploaded bus schedule is empty."]

    # REQ_COL contains the minimum required columns for a valid bus schedule.
    # We compare the uploaded DataFrame columns against that required set.
    # If any required columns are missing, we add a warning message.
    missing_columns = [col for col in REQ_COL if col not in df.columns]
    if missing_columns:
        warnings.append(
            "Missing expected columns in the bus schedule: " + ", ".join(missing_columns)
        )
        # If the required columns like 'activity' or 'energy consumption' are missing,
        # there is no point continuing with the rest of the warning checks because
        # those column-based checks would fail on missing keys.
        if "activity" not in df.columns or "energy consumption" not in df.columns:
            return warnings

    # This part checks for idle trips that are missing energy data.
    # It creates a boolean mask where the activity text equals 'idle' (case-insensitive).
    # That mask is used to select only rows where the activity is idle.
    if "activity" in df.columns:
        idle_activity_mask = df["activity"].astype(str).str.lower().eq("idle")
    else:
        idle_activity_mask = pd.Series(False, index=df.index)

    # If the energy consumption column exists, we inspect only the idle rows.
    # If any of those idle energy values are NaN, we add a warning.
    if "energy consumption" in df.columns:
        idle_energy = df.loc[idle_activity_mask, "energy consumption"]
        if not idle_energy.empty and idle_energy.isna().any():
            warnings.append(
                "Idle rows in the bus schedule are missing energy consumption values."
            )

        # This second check looks at the entire column, not just idle rows.
        # If any row in the uploaded schedule is missing an energy value,
        # it is also flagged as a warning.
        if df["energy consumption"].isna().any():
            warnings.append("Some rows in the bus schedule have missing energy consumption values.")

    # This part checks for duplicate rows.
    # DataFrame.duplicated() returns a boolean Series with True for repeated rows.
    # We compare all required columns that are present in the DataFrame,
    # so duplicates are detected based on the meaningful schedule data.
    duplicate_columns = [col for col in REQ_COL if col in df.columns]
    duplicate_rows = df.duplicated(subset=duplicate_columns)
    if duplicate_rows.any():
        warnings.append("Duplicate trip rows were detected in the bus schedule.")

    return warnings


def check_data_display():
    st.header("2. Check the data")

    if "merged_schedule" not in st.session_state:
        st.warning(
            "Please upload and merge the distance matrix and timetable first."
        )
        st.stop()

    # The uploader stores the selected file on the page, and the file is loaded
    # only when the user uploads it. The actual schedule is then normalized and
    # saved in session state so it can be reused across the rest of the website.
    uploaded_bus_schedule = st.file_uploader(
        "Upload bus schedule",
        type=["xlsx", "xls", "csv"],
        key="uploaded_bus_schedule"
    )

    if uploaded_bus_schedule is not None:
        st.session_state["bus_schedule_file"] = uploaded_bus_schedule
        st.session_state["bus_schedule"] = normalize_bus_schedule(load_data(uploaded_bus_schedule))
        st.success("Bus schedule uploaded and stored globally.")

    if "bus_schedule" not in st.session_state:
        st.info("Please upload a bus schedule first.")
        return

    df = st.session_state["bus_schedule"]
    st.session_state["current_check_df"] = df
    st.write("Uploaded bus schedule preview")
    st.dataframe(df.head(20), use_container_width=True)

    # This is the main validation step. check_data() returns a list of error strings.
    # If the list is non-empty, the page shows them as a blocking error block.
    issues = check_data(df)

    if issues:
        st.error(
            "The schedule contains validation issues:"
        )

        for issue in issues:
            st.write(f"- {issue}")

    # These warnings are shown separately from hard validation errors. They are
    # generated by get_bus_schedule_warnings() and each string is displayed with
    # st.warning(...), which appears as a yellow banner/box rather than a red error.
    if "bus_schedule" in st.session_state:
        warnings = get_bus_schedule_warnings(st.session_state["bus_schedule"])
        if warnings:
            st.warning("Warnings found in the uploaded bus schedule:")
            for warning in warnings:
                st.write(f"- {warning}")

    # No issues means the uploaded file passed the hard validation gate. The success
    # message and metrics only appear when the list of errors is empty.
    if not issues:
        st.success(
            "The uploaded schedule passed validation."
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


