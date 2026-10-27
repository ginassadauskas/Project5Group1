import streamlit as st
import pandas as pd

from busplanner.calculations.main import verify_schedule


def load_data(uploaded_file):
    """Load an uploaded schedule from CSV or Excel."""
    file_name = str(uploaded_file.name).lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if file_name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)

    raise ValueError(f"Unsupported file type: {uploaded_file.name}")


def check_data(df):
    """Run the project validator and return a list of issues if any."""
    validation = verify_schedule(
        filename="uploaded_schedule",
        timetable=pd.DataFrame(),
        dist_matrix=pd.DataFrame(),
        bus_plan=df,
    )

    if validation is True:
        return []
    if validation is False:
        return ["Schedule validation failed."]
    return [str(item) for item in validation]


def check_data_display():
    st.header("2. Check the data")

    if "merged_schedule" not in st.session_state:
        st.warning(
            "Please upload and merge the distance matrix and timetable first."
        )
        st.stop()

    df = st.session_state["merged_schedule"]

    issues = check_data(df)

    if issues:
        st.error(
            "The schedule contains validation issues:"
        )

        for issue in issues:
            st.write(f"- {issue}")
    else:
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


