"""File mistakes that cannot be fixed by the tool
"""
import pandas as pd
import numpy as np
from busplanner.calculations.defaults import CHARGER
from busplanner.calculations.power import energy_levels, safety_margin
from busplanner.calculations.imports import find_bustrip

def overlaps(bus_plan: pd.DataFrame, drop: bool=False):
    '''Checks for overlapping idle times for buses at the same location in the bus plan.

    [bus_plan] A finished bus schedule containing idle times with their start/end time/location and line.
    [drop] If true, the index of the resulting dataframe is reset. Default False

    [returns] A tuple. The first dataframe is waiting for the same line 
        at the same time as the corrosponding entry in the second DataFrame.
    '''
    # filter buses by ones that are actually idle, 
    #   then group by line, keeping only relevant columns.
    
    filtered = bus_plan.copy().loc[
        (bus_plan['activity'] == 'idle') & 
        (bus_plan['start location'].str not in CHARGER)
        ]
    filtered = filtered[['start time', 'end time', 'line', 'start location', 'end location']]

    left = filtered.reset_index(names="Duplicate")
    right = filtered.reset_index(names="With")

    pairs = left.merge(right, on="line", suffixes=(" 1", " 2"))

    overlaps = pairs[
        (pairs["Duplicate"] < pairs["With"])
        & (pairs["start time 1"] <= pairs["end time 2"])
        & (pairs["start time 2"] <= pairs["end time 1"])
        & (pairs['start location 1'] != pairs['start location 2'])
    ]

    if len(overlaps) == 0:
        return True
    else:
        overlaps['line__'] = overlaps['line']
        duplicate = overlaps[['start time 1', 'end time 1', 'line__', 'start location 1']]
        with_ = overlaps[['start time 2', 'end time 2', 'line__', 'start location 2']]
        duplicate.rename(columns = lambda x : str(x)[:-2])
        with_.rename(columns = lambda x : str(x)[:-2])
        return find_bustrip(duplicate, bus_plan, drop=drop), find_bustrip(with_, bus_plan, drop=drop)

def bus_teleport(bus_plan: pd.DataFrame): 
    '''
    Checks if the start location of a buses next trip matches the end location of its previous trip.

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for at least 'start location', 'end location', and 'bus'.

    Returns:
    ---------
    location_mismatches : list
        A list of dictionaries containing information about mismatches in start and end locations for each bus, including the bus identifier, previous end location, and current start location.
        also includes the start and end times to find the specific trip that has the issue.
    '''

    location_mismatches = []  # oh wow same thing as last time 

    for bus in bus_plan['bus'].unique():  # for every unique bus number
        sorted_plan = bus_plan[bus_plan['bus'] == bus].sort_values(by='start time')
        # sort by start time, technically not needed for this as with the previous one
        # just want to keep it generic 
        # general idea is that we take a bus then look at only the scedule for THAT bus

        for i in range(1, len(sorted_plan)):
            prev_row = sorted_plan.iloc[i - 1]
            curr_row = sorted_plan.iloc[i]
            # same idea as previous functions, I already mentioned this is a critical finding

            if prev_row['end location'] != curr_row['start location']:
                location_mismatches.append({
                    'bus': bus,
                    'end location': prev_row['end location'],
                    'start_location': curr_row['start location'],
                    'start time': curr_row['start time'],
                    'end time': curr_row['end time'],
                    # I think time is relevant for the client to check for issues
                })
    # verified with mismatch on rows 37 and 38 of the bus plan, so this function works as intended probably :p
    # also 18 mismatches to maybe relevant to the idling for 1 minute case 
    if len(location_mismatches) == 0:
        return True
    return find_bustrip(pd.DataFrame(location_mismatches))

def start_garage(bus_plan: pd.DataFrame):
    '''
    Checks if the first and last location of the whole schedule for each bus is the garage

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for at least 'end location' 'start location' and 'bus'.

    Returns:
    ---------
    garage_issues : pd.DataFrame
        Each entry with a bus that has a starting or ending location not in an available garage.
    '''

    garage_issues = []  # pretty much same with the template 

    for bus in bus_plan['bus'].unique():  # for every unique bus number
        sorted_plan = bus_plan[bus_plan['bus'] == bus].sort_values(by='start time')
        first_row = sorted_plan.iloc[0]
        last_row = sorted_plan.iloc[-1]

        if first_row['start location'] not in CHARGER:
            garage_issues.append(first_row)
        if last_row['end location'] not in CHARGER:
            garage_issues.append(last_row)

    # verified against data from the first 3 buses 

    if len(garage_issues) == 0:
        return True
    return pd.concat(garage_issues)

def Service_line(bus_plan: pd.DataFrame):
    '''
    Checks that every service trip has a non-empty line value.

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for at least 'line', 'activity', 'bus' and 'start time'

    Returns:
    ---------
    line_issues : list
        A list of issues with the start time of the trip and the bus number
    '''
    filtered = bus_plan[bus_plan['activity'] == 'service trip']
    missing_line = filtered[filtered['line'].isna()] 
    if len(missing_line) == 0:
        return True
    return missing_line

def validate_file_type(filename: str):
    return True if filename.endswith(('.xlsx', '.xls', '.csv')) else False
        #TypeError(f"'{filename}' is not an excel/csv file. Please insert an excel or csv file.")

def validate_energy(bus_plan):
    bus_plan = energy_levels(bus_plan)
    battery_level_errors = []

    for _, row in bus_plan.iterrows():
        if row['energy_level'] < safety_margin():
            print(type(row))
            battery_level_errors.append(row)

    if len(battery_level_errors) == 0:
        return True
    return pd.concat(battery_level_errors, axis=1).transpose().reset_index(drop=True)

print('checker: errors.py OK')