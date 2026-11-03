import sys
from pathlib import Path

import streamlit as st
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from busplanner.website.upload import load_data, upload_display
from busplanner.website.check import check_data_display
from busplanner.website.tutorial import show_tutorial, tutorial_button
from busplanner.website.optimize import optimize_display
from busplanner.website.results import results_display
from busplanner.website.comparison import comparison_display

st.set_page_config(
    page_title="Bus Schedule Optimizer",
    page_icon="🚌",
    layout="wide"
)


st.title("Bus Schedule Optimizer")

show_tutorial()
tutorial_button()

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
        "Optimize",
        "Results",
        "Comparison"
    ],
    index=0,
    horizontal=True
)


match step:
    case "Upload":
        upload_display()

    case "Check":
        check_data_display()

    case "Optimize":
        optimize_display()

    case "Results":
        results_display()

    case "Comparison":
        comparison_display()

    case _:
        st.error("Invalid step selected.")
        pass