import streamlit as st
import pandas as pd

from busplanner.calculations.imports import convert_time_to_minutes
from busplanner.calculations.main import verify_schedule


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
    if item is False:
        return "Validation failed."

    if isinstance(item, pd.Series):
        rows = [int(row) for row in item.index if row is not None]
        if not rows:
            return f"Validation issue in column '{item.name}'."
        return f"Validation issue in rows {rows[:10]} (column: {item.name})."

    if isinstance(item, pd.DataFrame):
        rows = [int(row) for row in item.index if row is not None]
        columns = list(item.columns)
        if not rows:
            return f"Validation issue in columns: {columns}."
        return f"Validation issue in rows {rows[:10]} and columns {columns}."

    if isinstance(item, (list, tuple)):
        return "; ".join(format_validation_issue(part) for part in item)

    return str(item)


def check_data(df):
    """Run the project validator and return a list of issues if any."""
    required_columns = [
        "bus",
        "start time",
        "end time",
        "start location",
        "end location",
        "activity",
        "line",
        "energy consumption",
    ]

    if df is None or not isinstance(df, pd.DataFrame):
        return ["The uploaded schedule is not a valid DataFrame."]

    df = normalize_bus_schedule(df)

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return [
            "The uploaded schedule is missing required columns: "
            + ", ".join(missing_columns)
        ]

    try:
        validation = verify_schedule(df)
    except KeyError as exc:
        return [f"Validation failed because the schedule is missing the required field: {exc.args[0]}"]
    except Exception as exc:  # pragma: no cover - for runtime safety in the UI
        return [f"Validation failed: {exc}"]

    if validation is True:
        return []
    if validation is False:
        return ["Schedule validation failed."]

    items = validation if isinstance(validation, (list, tuple)) else [validation]
    return [format_validation_issue(item) for item in items if item is not None]


def get_bus_schedule_warnings(df):
    """Return warning messages for uploaded bus schedule data."""
    warnings = []

    if df is None or df.empty:
        return ["The uploaded bus schedule is empty."]

    required_columns = [
        "bus",
        "start time",
        "end time",
        "start location",
        "end location",
        "activity",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        warnings.append(
            "Missing expected columns in the bus schedule: " + ", ".join(missing_columns)
        )

    if "energy consumption" in df.columns and df["energy consumption"].isna().any():
        warnings.append("Some rows in the bus schedule have missing energy consumption values.")

    duplicate_rows = df.duplicated(subset=[col for col in required_columns if col in df.columns])
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

    issues = check_data(df)

    if issues:
        st.error(
            "The schedule contains validation issues:"
        )

        for issue in issues:
            st.write(f"- {issue}")

    if "bus_schedule" in st.session_state:
        warnings = get_bus_schedule_warnings(st.session_state["bus_schedule"])
        if warnings:
            st.warning("Warnings found in the uploaded bus schedule:")
            for warning in warnings:
                st.write(f"- {warning}")

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


