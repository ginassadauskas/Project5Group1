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
        "Step 3: Generating a new schedule.",
        "Using the distance matrix and time table provided in step 1, generate a new bus plan.",
        "It uses an algorithm that tries to assign a bus as efficiently as possible throughout the day.",
        "It adds busses that each run efficiently until every service trips in the timetable has been assigned.",
        " ",
        "Step 4: Review the results of the algorithm.",
        "Display the schedule dirived in step 3 and compare it to the schedule uploaded in step 2.",
        "Both schedules are displayed in the form of a Gnatt chart and their KPI's.",
        "The KPI is primarily based of the number of busses used, with a small changes based of energy used as a tie breaker.",
        " ",
        "Step 5: Compare the old and new schedules.",
        " "
    ]

    for step in steps:
        if step == " ": #Empty line
            st.markdown(" ")
        else:
            st.markdown(f"- {step}")

    st.info("Tip: You can always reopen this tutorial from the sidebar.")

    if st.button("Got it"):
        st.session_state["tutorial_seen"] = True

@st.dialog("Welcome to the Bus Planner")
def tutorial_check(): # TODO Add multiple tutorial dialog options depending on which step the user is on. For example, if the user is on the "Upload" step, show a tutorial dialog that explains how to upload a file and what the expected format is. If the user is on the "Check" step, show a tutorial dialog that explains how to check the data and what to look for. If the user is on the "Optimize" step, show a tutorial dialog that explains how to optimize the schedule and what parameters can be adjusted. If the user is on the "Results" step, show a tutorial dialog that explains how to interpret the results and what metrics are important. If the user is on the "Comparison" step, show a tutorial dialog that explains how to compare different schedules and what to look for.
    st.markdown("### Schedule Check Explainations")
    st.write("Use this short walkthrough to get familiar with the app.")

    steps = [
        "Importing a finished bus schedule here checks for mistakes and shows them to you if any were found.",
        " ",
        "Due to time constraints, this step is unfortunalely manditory.",
        "In the next update, we will make it optional.",
        " ",
        "The following 11 checks are made by this website:",
        "Does the bus schedule miss any columns?",
        "Is each bus account for at all times?",
        "Do bus activities overlap with other activities at the same time?",
        "Does a bus start an activity where its last activity ended?",
        "Does each service trip have a valid service line?",
        "Is each bus entry one with a valid activity?",
        "Does each trip consume the correct amount of kW?",
        "Does each bus meet the safety SoC requirement?",
        "Does each bus start in a location with a charging spot?",
        "   WARNING: It is currently not possible to choose a charging spot and is assumed to be ehvgar.",
        "   We have a default settings page, but no way to access it from this website.",
        "Is each location visited by a bus one defined by the distance matrix?",
        "Is each service trip in the time table actually run by a bus?"
    ]

    for step in steps:
        if step == " ": #Empty line
            st.markdown(" ")
        else:
            st.markdown(f"- {step}")

    st.info("Tip: You can always reopen this tutorial from the sidebar.")

    if st.button("Got it"):
        st.session_state["tutorial_seen"] = True

@st.dialog("Welcome to the Bus Planner")
def tutorial_optimize(): # TODO Add multiple tutorial dialog options depending on which step the user is on. For example, if the user is on the "Upload" step, show a tutorial dialog that explains how to upload a file and what the expected format is. If the user is on the "Check" step, show a tutorial dialog that explains how to check the data and what to look for. If the user is on the "Optimize" step, show a tutorial dialog that explains how to optimize the schedule and what parameters can be adjusted. If the user is on the "Results" step, show a tutorial dialog that explains how to interpret the results and what metrics are important. If the user is on the "Comparison" step, show a tutorial dialog that explains how to compare different schedules and what to look for.
    st.markdown("### Optimization Stratagy")
    st.write("Use this short walkthrough to get familiar with the app.")

    steps = [
        "In this step, we will calculate a schedule from the Distance Matrix and Timetable given in step 1",
        "This tool uses a greedy constructive search, with the idea of using every bus as efficiently as possible.",
        " ",
        "After the calculation is complete, you can view the results in the next two steps.",
        "You can also download it from there.",
        " ",
        "Along with the code for this tool, you can find a document with the pseudo code as well.",
        "Here is an abridged version:",
        " ",
        "Step 1: Gather all requirements, such as a starting garage, power, and battery capacity per bus",
        "Step 2: Let the bus find the earlies service trips in the time table it can take.",
        "Step 2.5: Repeat step 2 for that bus until there are no more trips it can take because of its SoC or because there are no more service trips after it finishes.",
        "Step 2.55: If there are indeed no more service trips to take. Return the bus to a garage and skip step 3.",
        "Step 3: Return to the garage to charge. After it has sufficient power, take the bus and go back to step 2.",
        "Step 4: If there is at least one service trip that has not been assigned to a bus yet, take out a new bus, then repeat steps 2 to 4.",
        "Step 5: Calculate the final results and reveal them in results."
    ]

    for step in steps:
        if step == " ": #Empty line
            st.markdown(" ")
        else:
            st.markdown(f"- {step}")

    st.info("Tip: You can always reopen this tutorial from the sidebar.")

    if st.button("Got it"):
        st.session_state["tutorial_seen"] = True

@st.dialog("Welcome to the Bus Planner")
def tutorial_results(): # TODO Add multiple tutorial dialog options depending on which step the user is on. For example, if the user is on the "Upload" step, show a tutorial dialog that explains how to upload a file and what the expected format is. If the user is on the "Check" step, show a tutorial dialog that explains how to check the data and what to look for. If the user is on the "Optimize" step, show a tutorial dialog that explains how to optimize the schedule and what parameters can be adjusted. If the user is on the "Results" step, show a tutorial dialog that explains how to interpret the results and what metrics are important. If the user is on the "Comparison" step, show a tutorial dialog that explains how to compare different schedules and what to look for.
    st.markdown("### Result Layout")
    st.write("Use this short walkthrough to get familiar with the app.")

    steps = [
    ]

    for step in steps:
        if step == " ": #Empty line
            st.markdown(" ")
        else:
            st.markdown(f"- {step}")

    st.info("Tip: You can always reopen this tutorial from the sidebar.")

    if st.button("Got it"):
        st.session_state["tutorial_seen"] = True

@st.dialog("Welcome to the Bus Planner")
def tutorial_comparison(): # TODO Add multiple tutorial dialog options depending on which step the user is on. For example, if the user is on the "Upload" step, show a tutorial dialog that explains how to upload a file and what the expected format is. If the user is on the "Check" step, show a tutorial dialog that explains how to check the data and what to look for. If the user is on the "Optimize" step, show a tutorial dialog that explains how to optimize the schedule and what parameters can be adjusted. If the user is on the "Results" step, show a tutorial dialog that explains how to interpret the results and what metrics are important. If the user is on the "Comparison" step, show a tutorial dialog that explains how to compare different schedules and what to look for.
    st.markdown("### ?")
    st.write("Use this short walkthrough to get familiar with the app.")

    steps = [
        ""
        ""
        ""
        ""
    ]

    for step in steps:
        if step == " ": #Empty line
            st.markdown(" ")
        else:
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
