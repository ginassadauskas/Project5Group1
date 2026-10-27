"""File mistakes that can be solved by the tool
"""
import pandas as pd
def check_gaps(bus_plan: pd.DataFrame):
    '''
    Checks for gaps in the bus plan where a bus has a gap/overlap between its end time and the next start time.

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for at least 'start time', 'end time', and 'bus'.

    Returns:
    ---------
    gap_data : list
        A list of dictionaries containing information about gaps or overlaps for each bus, including the bus identifier, gap time, previous end time, and current start time.
    '''

    gap_data = []  # store rows with data for warning or error 

    for bus in bus_plan['bus'].unique(): # for every unique bus number
        sorted_plan = bus_plan[bus_plan['bus'] == bus].sort_values(by='start time')
        # sort by start time 

        for i in range(1, len(sorted_plan)):
            prev_row = sorted_plan.iloc[i - 1]
            curr_row = sorted_plan.iloc[i]
            gap = curr_row['start time'] - prev_row['end time']

            if gap != 0:  # if there is a gap (positive or negative)

                gap_data.append({ # write a dict of the data that has a positive or negative time gap
                    'bus': bus,
                    'gap_time': gap, # positive if there is a genuine gap, negative if overlap
                    'prev_end_time': prev_row['end time'],
                    'curr_start_time': curr_row['start time'],
                    # CAN technically modify this so you can input what data you want from warnings 
                    # or errors and then it will just output that data in a list of dicts for you to use however you want
                })
    return gap_data


def check_positive_negative_consumption(bus_plan: pd.DataFrame):
    '''

    '''
    consumption_issues = []

    for row in range(len(bus_plan)):
        if bus_plan.iloc[row]['energy consumption'] < 0 and bus_plan.iloc[row]['activity'] == 'charging':
            consumption_issues.append({
                'bus': bus_plan.iloc[row]['bus'],
                'start time': bus_plan.iloc[row]['start time'],
                'energy consumption': bus_plan.iloc[row]['energy consumption']
            })

        elif bus_plan.iloc[row]['energy consumption'] > 0 and bus_plan.iloc[row]['activity'] != 'charging':
            consumption_issues.append({
                'bus': bus_plan.iloc[row]['bus'],
                'start time': bus_plan.iloc[row]['start time'],
                'energy consumption': bus_plan.iloc[row]['energy consumption']
            })

    return consumption_issues

def validate_columns(
    bus_plan: pd.DataFrame,
    required_columns: list
):
    missing = set(required_columns) - set(bus_plan.columns)

    if missing:
        raise MissingColumnsError(
            f"Missing columns: {missing}. "
            "Please make sure all columns are inserted."
        )

def validate_locations(bus_plan: pd.DataFrame, allowed_locations):
    bad_start = bus_plan.loc[~bus_plan['start location'].isin(allowed_locations), 'start location']
    bad_end = bus_plan.loc[~bus_plan['end location'].isin(allowed_locations), 'end location']
    bad_values = set(bad_start.unique()) | set(bad_end.unique())
    if bad_values:
        raise InvalidLocationError(f"Unexpected location values found: {bad_values}. Are these locations correct?")

# check if there are any invalid activities
def validate_activities(bus_plan: pd.DataFrame, allowed_activities):
    bad_mask = ~bus_plan['activity'].isin(allowed_activities)
    if bad_mask.any():
        bad_values = bus_plan.loc[bad_mask, 'activity'].dropna().unique()
        raise InvalidActivityError(f"Invalid activities found: {list(bad_values)}. Allowed: {allowed_activities}")

# check if there are any activities that are empty
def validate_activity_not_empty(bus_plan: pd.DataFrame):
    empty_mask = bus_plan['activity'].isnull()
    if empty_mask.any():
        errors = [EmptyActivityError("activity field is empty", row=idx) for idx in bus_plan.index[empty_mask]]
        return errors
    return []

 
def validate_idle_energy(bus_plan: pd.DataFrame):
    errors = []
    idle = bus_plan[bus_plan['activity'] == 'idle']
    bad = idle[idle['energy consumption'] != 5]
    for idx in bad.index:
        errors.append(InvalidIdleEnergyError("idle activities must consume 5 energy", row=idx))
    return errors

def validate_line_numbers(bus_plan: pd.DataFrame):
    errors = []
    for idx, value in bus_plan['line'].items():
        if pd.isna(value):
            continue  # empty line is allowed
        numeric = pd.to_numeric(value, errors='coerce')
        if pd.isna(numeric):
            errors.append(InvalidLineNumberError(
                f"'{value}' is not a valid line number. Lines must be empty or numeric.", row=idx))
        elif len(str(int(numeric))) > 3:
            errors.append(InvalidLineNumberError(
                f"'{value}' has more than 3 digits.", row=idx))
    return errors
 
def validate_duplicate_schedule(bus_plan: pd.DataFrame):
    """Finds duplicate rows
    """
    errors = []
    subset_cols = ['bus', 'line', 'start time']
    duplicates = bus_plan[bus_plan.duplicated(subset=subset_cols, keep=False)]
    for idx, row in duplicates.iterrows():
        errors.append(DuplicateScheduleError(
            f"Duplicate bus/line/start time combo: bus {row['bus']}, line {row['line']}, "
            f"start {row['start time']}", row=idx))
    return errors


print('checker: warnings OK')