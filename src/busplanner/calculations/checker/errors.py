"""File mistakes that cannot be fixed by the tool
"""
import pandas as pd
import numpy as np
from busplanner.calculations.defaults import CHARGER
from busplanner.calculations.power import energy_levels, safety_margin

def overlaps(bus_plan: pd.DataFrame): #TODO WARNING at the bottom in the marked section 
    '''Checks for overlapping idle times for buses at the same location in the bus plan.

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for 'activity', 'start location', 'start time', 'end time', and 'bus'.

    Returns:
    ---------
    overlap_dict : dict
        A dict containing information about overlapping idle times, including the location, bus identifiers, and their respective start and end times.
    '''
    # filter buses by ones that are actually idle, 
    #   then group by line, keeping only relevant columns.

    print(bus_plan)
    
    filtered = bus_plan.copy().loc[
        (bus_plan['activity'].str == 'idle') & 
        (bus_plan['start location'].str not in CHARGER)
        ]
    filtered = filtered['start time', 'end time', 'line'].groupby('line')

    left = filtered.reset_index(names="Duplicate")
    right = filtered.reset_index(names="With")

    pairs = left.merge(right, on="bus", suffixes=(" 1", " 2"))

    overlaps = pairs[
        (pairs["Duplicate1"] < pairs["With"])
        & (pairs["start time 1"] <= pairs["end time 2"])
        & (pairs["Start time 2"] <= pairs["end time 1"])
    ]

    return overlaps


def check_start_end_location(bus_plan: pd.DataFrame): 
    
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
                    'prev_end_location': prev_row['end location'],
                    'curr_start_location': curr_row['start location'],
                    'start_time': curr_row['start time'],
                    'end_time': curr_row['end time'],
                    # I think time is relevant for the client to check for issues
                })
    # verified with mismatch on rows 37 and 38 of the bus plan, so this function works as intended probably :p
    # also 18 mismatches to maybe relevant to the idling for 1 minute case 
    return location_mismatches

def check_garage(bus_plan: pd.DataFrame):
    '''
    Checks if the first and last location of the whole schedule for each bus is the garage

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for at least 'end location' 'start location' and 'bus'.

    Returns:
    ---------
    garage_issues : list
        A list of dictionaries containing information about buses with the bus identifier, the issue (whether it's first or last trip), and the location in its place
    '''

    garage_issues = []  # pretty much same with the template 

    for bus in bus_plan['bus'].unique():  # for every unique bus number
        sorted_plan = bus_plan[bus_plan['bus'] == bus].sort_values(by='start time')

        last_row = sorted_plan.iloc[-1]  # get the last trip for this bus
        first_row = sorted_plan.iloc[0] # first trip lol 


        # run two checks for the first trip and last trip 

        if first_row['start location'] != 'ehvgar':
            garage_issues.append({'bus': bus,
                                  'issue': 'does not start at garage',
                                    'start_location': first_row['start location']
                                    })
        if last_row['end location'] != 'ehvgar':
            garage_issues.append({
                'bus': bus,
                'issue': 'does not end at garage',
                'end_location': last_row['end location']
                    })

    # verified against data from the first 3 buses 

    return garage_issues



def check_line_value(bus_plan: pd.DataFrame):
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
        line_issues = []

        filtered = bus_plan[bus_plan['activity'] == 'service trip']
        missing_line = filtered[filtered['line'].isna()] 

        for i in range(len(missing_line)):
            row = missing_line.iloc[i]
            line_issues.append(
                {
                    'bus': row['bus'],
                    'start time': row['start time'],
                }
            )

        # no such cases in the original data so can't verify but it does give like 380 values if 
        # I don't filter by service trip 
        return line_issues

def validate_file_type(filename: str):
    if not filename.endswith(('.xlsx', '.xls', '.csv')):
        return TypeError(f"'{filename}' is not an excel/csv file. Please insert an excel or csv file.")

def validate_energy(bus_plan):

    bus_plan = energy_levels(bus_plan) #Change to add battery consumption if necessary

    battery_level_errors = []

    for row in range(len(bus_plan)):
        if bus_plan.iloc[row]['energy_level'] < safety_margin():
            battery_level_errors.append({
                'bus': bus_plan.iloc[row]['bus'],
                'start time': bus_plan.iloc[row]['start time'],
                'energy_level': bus_plan.iloc[row]['energy_level']
            })

    return battery_level_errors