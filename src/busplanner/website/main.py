import sys
from pathlib import Path

import streamlit as st
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from busplanner.website.upload import load_data, upload_display
from busplanner.website.check import check_data_display
from busplanner.website.tutorial import tutorial_button
from busplanner.website.optimize import optimize_display
from busplanner.website.results import results_display
from busplanner.website.comparison import comparison_display

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

st.session_state['step'] = "Upload"
tutorial_button()

step = st.radio(
    "Step",
    [
        "Upload",
        "Check",
        "Optimize",
        "Results",
        "Comparison"
    ],
    index=0,
    horizontal=True
)

match step:
    case "Upload":
        st.session_state['step'] = "Upload"
        upload_display()

    case "Check":
        st.session_state['step'] = "Check"
        check_data_display()
        
    case "Optimize":
        st.session_state['step'] = "Optimize"
        optimize_display()
        
    case "Results":
        st.session_state['step'] = "Results"
        results_display()
        
    case "Comparison":
        st.session_state['step'] = "Comparison"
        comparison_display()
        
    case _:
        st.error("Invalid step selected.")
        pass

