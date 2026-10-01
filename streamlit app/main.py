import streamlit as st
import pandas as pd

st.write(
    "Please input your bus schedule here. Please note it must be an Excel or CSV file "
    "and have the columns of: [required columns]"
)

st.write(
    "When uploading the bus schedule, you agree to the terms and conditions "
    "of using this service."
)

st.write(
    "Upon reading the bus schedule, the system will process the data and provide "
    "you an optimal bus schedule based on your input. Please ensure that the data "
    "is accurate and complete to get the best results."
)

bus_schedule = st.file_uploader(
    "Upload File",
    type=["xlsx", "xls", "csv"],
    key="profile_upload",
    help="Upload your bus schedule here."
)

if bus_schedule is not None:

    # Read the uploaded file depending on its type
    if bus_schedule.name.endswith(".csv"):
        df = pd.read_csv(bus_schedule)
    else:
        df = pd.read_excel(bus_schedule)

    # Show the imported file
    st.write("### Imported Bus Schedule")
    st.dataframe(df, use_container_width=True)


# show the errors that it found and how it changed them.
