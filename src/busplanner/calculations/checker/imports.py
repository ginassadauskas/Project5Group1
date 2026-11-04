import pandas as pd
from busplanner.calculations.defaults import (
    normalize_bus_plan_columns,
    normalize_location_name,
)
from ..imports import convert_time_to_minutes

def convert_empty_line_to_next(bus_plan: pd.DataFrame):
    '''
    Converts empty line values in the bus plan to the next available line value for the same bus.

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for at least 'line', 'bus', and 'start time'.

    Returns:
    ---------
    bus_plan : pd.Series
        The bus plan line column with empty line values filled with the next available line value for the same bus.

    >>> test_data = pd.DataFrame({
    ...     'bus': [1, 1, 1],
    ...     'start time': [0, 10, 20],'line': [None, 401, None],
    ... })
    >>> list(convert_empty_line_to_next(test_data))
    [401.0, 401.0, -1.0]
    '''
    bus_plan = bus_plan.copy()
    bus_plan = bus_plan.sort_values(by=['bus', 'start time'])
    filled = bus_plan['line'] = bus_plan.groupby('bus')['line'].bfill() 
    #bfill does exactly the thing I need in a single function

    return filled.fillna(-1)  # fill any remaining NaN values with -1 to indicate no line available

def import_bus_plan(bus_plan: pd.DataFrame):
    """Imports and prepares the bus plan for further processing.
    """
    bus_plan = normalize_bus_plan_columns(bus_plan.copy())

    if 'start location' in bus_plan.columns:
        bus_plan['start location'] = bus_plan['start location'].map(normalize_location_name)
    if 'end location' in bus_plan.columns:
        bus_plan['end location'] = bus_plan['end location'].map(normalize_location_name)

    if 'start time' not in bus_plan.columns or 'end time' not in bus_plan.columns:
        missing = sorted({"start time", "end time"} - set(bus_plan.columns))
        raise KeyError(f"Missing required time columns in uploaded bus schedule: {missing}")

    bus_plan['start time'] = convert_time_to_minutes(bus_plan['start time'])
    bus_plan['end time'] = convert_time_to_minutes(bus_plan['end time'])
    bus_plan['line'] = convert_empty_line_to_next(bus_plan)
    bus_plan['duration'] = bus_plan['end time'] - bus_plan['start time']
    return bus_plan


print('checker: imports OK')