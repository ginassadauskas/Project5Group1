import streamlit as st
import pandas as pd


def optimize_display():
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
        optimized_df = optimize_schedule( # put in a real function that optimizes the schedule based on the cleaned dataframe
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


optimize_display()