import streamlit as st


@st.dialog("Welcome to the Bus Planner")
def tutorial_dialog(): # TODO Add multiple tutorial dialog options depending on which step the user is on. For example, if the user is on the "Upload" step, show a tutorial dialog that explains how to upload a file and what the expected format is. If the user is on the "Check" step, show a tutorial dialog that explains how to check the data and what to look for. If the user is on the "Optimize" step, show a tutorial dialog that explains how to optimize the schedule and what parameters can be adjusted. If the user is on the "Results" step, show a tutorial dialog that explains how to interpret the results and what metrics are important. If the user is on the "Comparison" step, show a tutorial dialog that explains how to compare different schedules and what to look for.
    st.markdown("### Quick start guide")
    st.write("Use this short walkthrough to get familiar with the app.")

    steps = [
        "Welcome to the busplanner. You can open this tutorial at any time in the upper left corner",
        "In step 1, this tutorial explains to you how to use the website.",
        "In all other steps, it gives tips and gives more information on what the website does.",
        " ",
        "The website exists of 4 steps, all of them manditory to generate a schedule",
        "In a future update, we plan to make step 2 optional. Currently it is a dependancy of step 4.",
        " ",
        "Step 1: Uploading Bus environment.",
        "Upload the distance matrix and time table.",
        "These are used for checking errors in step 2 and to create a new schedule in step 3",
        " ",
        "Step 2: Check for errors in a completed schedule.",
        "Upload a completed bus schedule compatible with the distance matrix and timetable given in step 1.",
        "The bus schedule will be checked for errors, such as an unkown line or incorrect power consumption.",
        "If the website finds any errors, it notifies you of the nature and location of the error.",
        "The website will also estimate and correct incorrect power consumptions in the given schedule",
        " ",
        "Step 3. Generating a new schedule.",
        "Using the distance matrix and time table provided in step 1, generate a new bus plan.",
        "It uses an algorithm that tries to assign a bus as efficiently as possible throughout the day.",
        "It adds busses that each run efficiently until every service trips in the timetable has been assigned.",
        " ",
        "Step 4. Review the results and compare the outcomes.",
        "Display the schedule dirived in step 3 and compare it to the schedule uploaded in step 2.",
        "Both schedules are displayed in the form of a Gnatt chart and their KPI's.",
        "The KPI is primarily based of the number of busses used, with a small changes based of energy used as a tie breaker."
    ]

    for step in steps:
        if step == " ": #Empty line
            st.markdown(" ")
        st.markdown(f"- {step}")

    st.info("Tip: You can always reopen this tutorial from the sidebar.")

    if st.button("Got it"):
        st.session_state["tutorial_seen"] = True

def tutorial_check(): # TODO Add multiple tutorial dialog options depending on which step the user is on. For example, if the user is on the "Upload" step, show a tutorial dialog that explains how to upload a file and what the expected format is. If the user is on the "Check" step, show a tutorial dialog that explains how to check the data and what to look for. If the user is on the "Optimize" step, show a tutorial dialog that explains how to optimize the schedule and what parameters can be adjusted. If the user is on the "Results" step, show a tutorial dialog that explains how to interpret the results and what metrics are important. If the user is on the "Comparison" step, show a tutorial dialog that explains how to compare different schedules and what to look for.
    st.markdown("### Schedule Check Explainations")
    st.write("Use this short walkthrough to get familiar with the app.")

    steps = [
        "1. Upload the distance matrix and time table.",
        "2. Check the merged schedule for any issues or warnings.",
        "3. Clean the data if needed before continuing.",
        "4. Optimize the timetable to improve the schedule.",
        "5. Review the results and compare the outcomes.",
    ]

    for step in steps:
        if step == " ": #Empty line
            st.markdown(" ")
        st.markdown(f"- {step}")

    st.info("Tip: You can always reopen this tutorial from the sidebar.")

    if st.button("Got it"):
        st.session_state["tutorial_seen"] = True

def tutorial_optimize(): # TODO Add multiple tutorial dialog options depending on which step the user is on. For example, if the user is on the "Upload" step, show a tutorial dialog that explains how to upload a file and what the expected format is. If the user is on the "Check" step, show a tutorial dialog that explains how to check the data and what to look for. If the user is on the "Optimize" step, show a tutorial dialog that explains how to optimize the schedule and what parameters can be adjusted. If the user is on the "Results" step, show a tutorial dialog that explains how to interpret the results and what metrics are important. If the user is on the "Comparison" step, show a tutorial dialog that explains how to compare different schedules and what to look for.
    st.markdown("### Optimization Stratagy")
    st.write("Use this short walkthrough to get familiar with the app.")

    steps = [
    ]

    for step in steps:
        if step == " ": #Empty line
            st.markdown(" ")
        st.markdown(f"- {step}")

    st.info("Tip: You can always reopen this tutorial from the sidebar.")

    if st.button("Got it"):
        st.session_state["tutorial_seen"] = True

def tutorial_results(): # TODO Add multiple tutorial dialog options depending on which step the user is on. For example, if the user is on the "Upload" step, show a tutorial dialog that explains how to upload a file and what the expected format is. If the user is on the "Check" step, show a tutorial dialog that explains how to check the data and what to look for. If the user is on the "Optimize" step, show a tutorial dialog that explains how to optimize the schedule and what parameters can be adjusted. If the user is on the "Results" step, show a tutorial dialog that explains how to interpret the results and what metrics are important. If the user is on the "Comparison" step, show a tutorial dialog that explains how to compare different schedules and what to look for.
    st.markdown("### Result Layout")
    st.write("Use this short walkthrough to get familiar with the app.")

    steps = [
    ]

    for step in steps:
        if step == " ": #Empty line
            st.markdown(" ")
        st.markdown(f"- {step}")

    st.info("Tip: You can always reopen this tutorial from the sidebar.")

    if st.button("Got it"):
        st.session_state["tutorial_seen"] = True

def tutorial_comparison(): # TODO Add multiple tutorial dialog options depending on which step the user is on. For example, if the user is on the "Upload" step, show a tutorial dialog that explains how to upload a file and what the expected format is. If the user is on the "Check" step, show a tutorial dialog that explains how to check the data and what to look for. If the user is on the "Optimize" step, show a tutorial dialog that explains how to optimize the schedule and what parameters can be adjusted. If the user is on the "Results" step, show a tutorial dialog that explains how to interpret the results and what metrics are important. If the user is on the "Comparison" step, show a tutorial dialog that explains how to compare different schedules and what to look for.
    st.markdown("### ?")
    st.write("Use this short walkthrough to get familiar with the app.")

    steps = [
        "1. Upload the distance matrix and time table.",
        "2. Check the merged schedule for any issues or warnings.",
        "3. Clean the data if needed before continuing.",
        "4. Optimize the timetable to improve the schedule.",
        "5. Review the results and compare the outcomes.",
    ]

    for step in steps:
        if step == " ": #Empty line
            st.markdown(" ")
        st.markdown(f"- {step}")

    st.info("Tip: You can always reopen this tutorial from the sidebar.")

    if st.button("Got it"):
        st.session_state["tutorial_seen"] = True

def tutorial_button():
    """Add a helper button to reopen the tutorial later."""
    st.write("Made by Team 1 - Fontys University of Applied Sciences")
    st.write("Emily, Casper, & Ginas")
    if st.sidebar.button("Open tutorial"):
        match st.session_state["step"]:
            case "Upload":
                tutorial_dialog()
            case "Check":
                tutorial_check()
            case "Optimize":
                tutorial_optimize()
            case "Results":
                tutorial_results()
            case "Comparison":
                tutorial_comparison()

if __name__ == "__main__":
    st.title("Tutorial Popup!")
    tutorial_button()
