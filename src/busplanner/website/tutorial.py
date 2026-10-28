import streamlit as st


@st.dialog("Welcome to the Bus Planner")
def tutorial_dialog():
    st.markdown("### Quick start guide")
    st.write("Use this short walkthrough to get familiar with the app.")

    steps = [
        "1. Upload the distance matrix and time table.",
        "2. Check the merged schedule for any issues or warnings.",
        "3. Clean the data if needed before continuing.",
        "4. Optimize the timetable to improve the schedule.",
        "5. Review the results and compare the outcomes.",
    ]

    for step in steps:
        st.markdown(f"- {step}")

    st.info("Tip: You can always reopen this tutorial from the sidebar.")

    if st.button("Got it"):
        st.session_state["tutorial_seen"] = True


def show_tutorial():
    """Open the popup only on the first run of the app."""
    if "tutorial_seen" not in st.session_state:
        st.session_state["tutorial_seen"] = True


def tutorial_button():
    """Add a helper button to reopen the tutorial later."""
    st.write("Made by Team 1 - Fontys University of Applied Sciences")
    st.write("Emily, Casper, & Ginas")
    if st.sidebar.button("Open tutorial"):
        tutorial_dialog()


if __name__ == "__main__":
    st.title("Tutorial test")
    show_tutorial()
    tutorial_button()
