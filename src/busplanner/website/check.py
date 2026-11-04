import streamlit as st
import pandas as pd

from busplanner.calculations.checker import main as checker
from busplanner.calculations.checker.imports import import_bus_plan
from busplanner.calculations.checker.warning import correct_consumption
from busplanner.calculations.defaults import REQ_COL


def load_data(uploaded_file):
    """Load an uploaded schedule from CSV or Excel."""
    # Streamlit gives us a file-like object from st.file_uploader.
    # We inspect the extension from uploaded_file.name and then use pandas to read it.
    file_name = str(uploaded_file.name).lower()

    if file_name.endswith(".csv"):
        return import_bus_plan(pd.read_csv(uploaded_file))
    if file_name.endswith((".xlsx", ".xls")):
        return import_bus_plan(pd.read_excel(uploaded_file))

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
    warnings = []

    if df is None or df.empty:
        return ["The uploaded bus schedule is empty."]

    missing_columns = sorted(set(REQ_COL) - set(df.columns))
    if missing_columns:
        warnings.append(
            "Missing expected columns in the bus schedule: " + ", ".join(missing_columns)
        )
        return warnings

    if "activity" in df.columns and "energy consumption" in df.columns:
        idle_activity_mask = df["activity"].astype(str).str.lower().eq("idle")
        idle_energy = df.loc[idle_activity_mask, "energy consumption"]
        if not idle_energy.empty and idle_energy.isna().any():
            warnings.append(
                "Idle rows in the bus schedule are missing energy consumption values."
            )

        if df["energy consumption"].isna().any():
            warnings.append("Some rows in the bus schedule have missing energy consumption values.")

    duplicate_columns = [col for col in REQ_COL if col in df.columns]
    if duplicate_columns:
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
        st.session_state["bus_schedule"] = load_data(uploaded_bus_schedule)
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

    charge_issues = checker.val_energy(df) # TODO
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


