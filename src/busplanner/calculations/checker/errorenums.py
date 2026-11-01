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

def error_all_service_ran(errorlines):
    pass

def error_validate_locations(errorlines):
    pass

def error_validate_line_numbers(errorlines):
    pass


class BusScheduleError(Exception):
    """Base class for every error this validator can raise."""

    def __init__(self, message, row=None):
        self.row = row
        if row is not None:
            message = f"[Row {row}] {message}"
        super().__init__(message)

class InvalidFileTypeError(BusScheduleError):
    """The uploaded file isn't a .csv, .xlsx, or .xls file."""

class MissingColumnsError(BusScheduleError):
    """One or more required columns are missing. Uses hard values"""

class InvalidLocationError(BusScheduleError):
    """A start/end location isn't in the allowed list."""
   
class SameLocationError(BusScheduleError):
    """Start location and end location are identical for a row."""

class InvalidActivityError(BusScheduleError):
    """An activity value isn't one of the allowed activities."""


class EmptyActivityError(BusScheduleError):
    """The activity field is empty."""


class InvalidEnergyValueError(BusScheduleError):
    """Energy consumption isn't a valid number."""


class InvalidIdleEnergyError(BusScheduleError):
    """An idle activity doesn't consume exactly 5 energy."""


class InvalidLineNumberError(BusScheduleError):
    """Line isn't numeric, or has more than 3 digits."""


class DuplicateScheduleError(BusScheduleError):
    """There are duplicate rows"""
                
class ScheduleValidationError(BusScheduleError):
    """Aggregates every row-level error found in one validation pass."""

    def __init__(self, errors):
        self.errors = errors
        message = f"{len(errors)} validation error(s) found:\n" + "\n".join(
            f" - {e}" for e in errors
        )
        super().__init__(message)

print('checker: errorenums.py OK')