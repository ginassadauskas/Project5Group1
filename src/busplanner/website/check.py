import streamlit as st
import pandas as pd

from busplanner.calculations.imports import normalize_schedule_values
from busplanner.calculations.checker import main as checker
from busplanner.calculations.checker.warning import correct_consumption
from busplanner.calculations.checker.errors import validate_energy
from busplanner.calculations.defaults import REQ_COL

def normalize_bus_schedule(df):
    """Convert time-like columns to minute values before validation."""
    return normalize_schedule_values(df)


def load_data(uploaded_file):
    """Load an uploaded schedule from CSV or Excel."""
    # Streamlit gives us a file-like object from st.file_uploader.
    # We inspect the extension from uploaded_file.name and then use pandas to read it.
    file_name = str(uploaded_file.name).lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if file_name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)

    raise ValueError(f"Unsupported file type: {uploaded_file.name}")


def format_validation_issue(item):
    """Convert raw checker output into a short user-facing issue describing row/column locations."""
    # This function converts the raw return values from the project validator
    # into messages that are easy to display in Streamlit.
    # The validator often returns pandas Series/DataFrames, and this function extracts the indices
    # and column names so the user can see where the issue occurred.
    if item is True:
        return "No validation issues found."
    elif item is False:
        return "Validation failed."

    if isinstance(item, pd.Series):
        # A pandas Series means one column is problematic.
        rows = [int(row) for row in item.index if row is not None]
        if not rows:
            return f"Validation issue in column '{item.name}'."
        return f"Validation issue in rows {rows[:10]} (column: {item.name})."

    if isinstance(item, pd.DataFrame):
        # A DataFrame means multiple fields are involved, so we report the row numbers and column names.
        rows = [int(row) for row in item.index if row is not None]
        columns = list(item.columns)
        if not rows:
            return f"Validation issue in columns: {columns}."
        return f"Validation issue in rows {rows[:10]} and columns {columns}."

    if isinstance(item, (list, tuple)):
        # Nested validator output is flattened recursively so all issues appear in one readable list.
        return "; ".join(format_validation_issue(part) for part in item)
    else:
        return str(item)

def get_bus_schedule_warnings(df: pd.DataFrame):
    """Return warning messages for uploaded bus schedule data."""
    # Warnings are not hard validation errors. They are softer quality checks meant to tell the user
    # that something may need manual attention without blocking the whole page.
    warnings = []

    # This function does not raise an exception or stop the page. It simply
    # builds a Python list of warning strings. That list is later checked in the
    # Streamlit page, and if it's not empty the page calls st.warning(...)
    # and prints each message one by one.
    # So this is the "preparation stage" for warnings before the website displays them.
    if df is None or df.empty:
        return ["The uploaded bus schedule is empty."]

    if "activity" not in df.columns or "energy consumption" not in df.columns:
        return warnings

    # pandas boolean masks are used here to find all rows where the activity is idle.
    idle_activity_mask = df["activity"].astype(str).str.lower().eq("idle")
    idle_energy = df.loc[idle_activity_mask, "energy consumption"]

    # If any idle trip is missing an energy value, show a warning only for those rows.
    if not idle_energy.empty and idle_energy.isna().any():
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
    # This is the main Streamlit page function for the validation step.
    # It uses st.session_state to remember uploaded files across reruns, because Streamlit reruns
    # the script every time the user interacts with widgets.
    issues = False
    st.header("2. Check & clean the data")

    if "merged_schedule" not in st.session_state:
        st.warning(
            "Please upload and merge the distance matrix and timetable first."
        )
        st.stop()

    # Streamlit widget: a file uploader with allowed Excel/CSV types.
    # It returns a file object, not a DataFrame, so the app then calls load_data() to convert it.
    uploaded_bus_schedule = st.file_uploader(
        "Upload bus schedule",
        type=["xlsx", "xls", "csv"],
        key="uploaded_bus_schedule"
    )

    if uploaded_bus_schedule is not None:
        # This stores the uploaded file and the parsed DataFrame in session_state so they persist
        # across reruns within the same browser session.
        st.session_state["bus_schedule_file"] = uploaded_bus_schedule
        st.session_state["bus_schedule"] = normalize_bus_schedule(load_data(uploaded_bus_schedule))
        st.success("Bus schedule uploaded and stored globally.")

    if "bus_schedule" not in st.session_state:
        # The user has not uploaded a file yet, so stop this function early.
        st.info("Please upload a bus schedule first.")
        return

    df = st.session_state["bus_schedule"]
    st.session_state["current_check_df"] = df

    # Display a preview of the DataFrame as a table using pandas + Streamlit.
    st.write("Uploaded bus schedule preview")
    st.dataframe(df.head(20), use_container_width=True)

    # This is the strict validation pass: it returns a list of serious issues.
    busplan_issues = checker.verify_bus(df) # TODO add the checks from calculations/checker/main.py to this function so that it returns a list of issues if any
    if busplan_issues is not True:
        issues = True
        # st.error gives red text and is intended for blocking validation issues.
        st.error(
            "The schedule contains isolated issues:"
        )

        for issue in busplan_issues:
            st.write(f"- {issue}")

    # This is the strict validation pass: it returns a list of serious issues.
    schedule_issues = checker.verify_critical(df, st.session_state["distance_matrix"], st.session_state["merged_schedule"]) # TODO
    if schedule_issues is not True:
        issues = True
        # st.error gives red text and is intended for blocking validation issues.
        st.error(
            "The schedule contains conflicts with the timetable and/or distance matrix:"
        )

        for issue in schedule_issues:
            st.write(f"- {issue}")

    consumption_issues = correct_consumption(df, st.session_state["distance_matrix"]) # TODO
    if consumption_issues is not True:
        issues = True
        # st.error gives red text and is intended for blocking validation issues.
        st.warning(
            "The schedule contains incorrect power consumptions and have been adjusted:"
        )

        df = consumption_issues[1]

        for issue in consumption_issues[0]:
            st.write(f"- {issue}")

    charge_issues = validate_energy(df) # TODO
    if charge_issues is not True:
        issues = True
        # st.error gives red text and is intended for blocking validation issues.
        st.error(
            "The schedule contains buses that fall below the allowed safety margin:"
        )

        for issue in charge_issues:
            st.write(f"- {issue}")

    # This is the warning-only pass. These are not blockers, only quality notices.
    if "bus_schedule" in st.session_state:
        warnings = get_bus_schedule_warnings(st.session_state["bus_schedule"])
        if warnings:
            # st.warning creates a yellow warning box, which is appropriate for non-blocking issues.
            st.warning("Warnings found in the uploaded bus schedule:")
            for warning in warnings:
                st.write(f"- {warning}")

    # No issues means the uploaded file passed the hard validation gate. The success
    # message and metrics only appear when the list of errors is empty.
    if issues is not True:
        # A successful validation result is displayed in green.
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


