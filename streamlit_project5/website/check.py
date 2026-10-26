import streamlit as st
import pandas as pd


def check_data_display():
    st.header("2. Check the data")

    if "uploaded_file" not in st.session_state:
        st.warning(
            "Please upload a file first."
        )
        st.stop()

    df = load_data(
        st.session_state["uploaded_file"]
    )

    missing = check_data(df) # put in a real function that checks the data for any errors or serious things missing

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


check_data_display()

