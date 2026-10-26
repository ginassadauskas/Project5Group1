import streamlit as st
import pandas as pd
import 

st.set_page_config(
    page_title="Bus Schedule Optimizer",
    page_icon="🚌",
    layout="wide"
)


st.title("Bus Schedule Optimizer")

st.write(
    "Upload a schedule and go through the different "
    "steps to create an improved timetable."
)

st.divider()
 # dummy functions removed

step = st.radio(
    "Step",
    [
        "Upload",
        "Check",
        "Clean",
        "Optimize",
        "Results",
        "Comparison"
    ],
    horizontal=True
)


# ---------------------------------------------------------
# UPLOAD
# ---------------------------------------------------------

match step:
    case "Upload":
        # call functions from upload.py
        pass

    
# ---------------------------------------------------------
# CHECK
# ---------------------------------------------------------

    case "Check":

        # call functions from check.py
# ---------------------------------------------------------
# CLEAN
# ---------------------------------------------------------

    case "Clean":

        # call functions from clean.py

# ---------------------------------------------------------
# OPTIMIZE
# ---------------------------------------------------------

    case "Optimize":

        # call functions from optimize.py



    case "Results":

        # call functions from results.py


    case "Comparison":

        # call functions from comparison.py



    case "Optimize":
        # call functions from optimize.py


    case "Results":
        # call functions from results.py


    case "Comparison":
        # call functions from comparison.py

    case _:
        st.error("Invalid step selected.")