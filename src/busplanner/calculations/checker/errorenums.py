from typing import Any
import pandas as pd

## verify_bus()
def error_activity_none_empty(errorlines: pd.DataFrame):
    ers = []

    for index, haserror in errorlines.iterrows():
        if haserror:
            ers.append(f'Bus found without an activity at index {index}')

    return ers

        
def error_validate_activities(errorlines: set):
    ers = []

    for activity in errorlines:
        ers.append(f'Unknown activity {activity}')

    return ers


def error_service_line(errorlines: pd.DataFrame):
    ers = []

    for index, row in errorlines:
        ers.append(f'A bus at index {index} is running a service trip without a line.')

    return ers

def error_gaps(errorlines: pd.DataFrame):
    ers = []
    prev_index = 0

    for index, row in errorlines:
        ers.append(f'''Bus {row['bus']} start ({row['start time']}) and previous end 
                   ({row['end times']}) times do not match. (Line {index} and {prev_index})''')
        prev_index = index

    return ers

def error_bus_teleport(errorlines: list[dict]):
    ers = []

    for error in errorlines:
        ers.append(f'Bus {error['bus']} starts its activity of {error['start time']} at location {error['start location']}, but ended its last activity in {error["end location"]}.')

    return ers

def error_all_service_ran(errorlines: pd.DataFrame):
    ers = []

    for _, error in errorlines.iterrows():
        ers.append(f'No bus rides the service trip that was supposed to start at {error['start time']} and line {error['line']}.')

    return ers

def error_validate_locations(errorlines: set):
    ers = []

    for error in errorlines:
        ers.append(f'Location {error} is not known in the distance matrix.')

    return ers

def error_validate_line_numbers(errorlines):
    ers = []

    for error in errorlines:
        ers.append(f'Line {error} is not known in the distance matrix')

    return ers

def error_validate_energy(errorlines: pd.DataFrame):
    ers = []

    for index, error in errorlines.iterrows():
        ers.append(f'Bus {error['bus']} runs out of charge at line {index}.')

    return ers


def warning_start_garage(errorlines: pd.DataFrame):
    ers = []

    for _, error in errorlines.iterrows():
        ers.append(f'Bus {error['bus']} does not start or end in a garage.')

    return ers

print('checker: errorenums.py OK')