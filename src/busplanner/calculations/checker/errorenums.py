from typing import Any
import pandas as pd
from busplanner.calculations.imports import cmh

## verify_bus()
def error_activity_none_empty(errorlines: pd.DataFrame):
    ers = []

    for _, haserror in errorlines.iterrows():
        if haserror:
            ers.append(f'Bus found without an activity at start time {cmh(haserror['start time'])}')

    return ers

        
def error_validate_activities(errorlines: set):
    ers = []

    for activity in errorlines:
        ers.append(f'Unknown activity {activity}')

    return ers


def error_service_line(errorlines: pd.DataFrame):
    ers = []

    for _, row in errorlines:
        ers.append(f'A bus at start time {cmh(row['start time'])} is running a service trip without a line.')

    return ers

def error_gaps(errorlines: pd.DataFrame):
    ers = []

    for _, row in errorlines.iterrows():
        ers.append(f'''Bus {row['bus']} start ({cmh(row['start time'])}) and previous end 
                   ({cmh(row['end time'])}) times do not match.''')

    return ers

def error_bus_teleport(errorlines: list[dict]):
    ers = []

    for error in errorlines:
        ers.append(f'Bus {error['bus']} starts its activity of {cmh(error['start time'])} at location {error['start location']}, but ended its last activity in {error["end location"]}.')

    return ers

def error_all_service_ran(errorlines: pd.DataFrame):
    ers = []

    for _, error in errorlines.iterrows():
        ers.append(f'No bus rides the service trip that was supposed to start at {cmh(error['start time'])} and line {error['line']}.')

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

    for _, error in errorlines.iterrows():
        ers.append(f'Bus {error['bus']} runs out of charge at start time {cmh(error['start time'])}.')

    return ers


def warning_start_garage(errorlines: pd.DataFrame):
    ers = []

    for _, error in errorlines.iterrows():
        ers.append(f'Bus {error['bus']} does not start or end in a garage.')

    return ers

print('checker: errorenums.py OK')