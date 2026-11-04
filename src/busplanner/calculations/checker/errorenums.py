from typing import Any
import pandas as pd
from busplanner.calculations.imports import cmh


def _safe_time(value):
    """Return a readable time string from a numeric minute value or a row value."""
    if value is None or pd.isna(value):
        return "unknown time"
    if isinstance(value, (int, float)):
        return cmh(value)
    if isinstance(value, str):
        try:
            return cmh(float(value))
        except ValueError:
            return value
    return str(value)


## verify_bus()
def error_activity_none_empty(errorlines: pd.Series | pd.DataFrame):
    ers = []

    if isinstance(errorlines, pd.Series):
        for idx, haserror in errorlines.items():
            if haserror:
                ers.append(f"Bus found without an activity at row index {idx}.")
        return ers

    for _, row in errorlines.iterrows():
        if row.to_numpy().any():
            continue

    return ers


def error_validate_activities(errorlines: set):
    ers = []

    for activity in errorlines:
        ers.append(f"Unknown activity {activity}")

    return ers


def error_service_line(errorlines: pd.DataFrame):
    ers = []

    for _, row in errorlines.iterrows():
        ers.append(f"A bus at start time {_safe_time(row['start time'])} is running a service trip without a line.")

    return ers


def error_gaps(errorlines: pd.DataFrame):
    ers = []

    for _, row in errorlines.iterrows():
        ers.append(f"Bus {row['bus']} start ({_safe_time(row['start time'])}) and previous end ({_safe_time(row['end time'])}) times do not match.")

    return ers


def error_bus_teleport(errorlines: list[dict]):
    ers = []

    for error in errorlines:
        ers.append(
            f"Bus {error['bus']} starts its activity of {_safe_time(error['start time'])} at location {error['start location']}, but ended its last activity in {error['end location']} ."
        )

    return ers


def error_all_service_ran(errorlines: pd.DataFrame):
    ers = []

    for _, error in errorlines.iterrows():
        ers.append(f"No bus rides the service trip that was supposed to start at {_safe_time(error['start time'])} and line {error['line']}.")

    return ers


def error_validate_locations(errorlines: set):
    ers = []

    for error in errorlines:
        ers.append(f"Location {error} is not known in the distance matrix.")

    return ers


def error_validate_line_numbers(errorlines):
    ers = []

    for error in errorlines:
        ers.append(f"Line {error} is not known in the distance matrix")

    return ers


def error_validate_energy(errorlines: pd.DataFrame):
    ers = []

    for _, error in errorlines.iterrows():
        ers.append(f"Bus {error['bus']} runs out of charge at start time {_safe_time(error['start time'])}.")

    return ers


def warning_start_garage(errorlines):
    ers = []

    if isinstance(errorlines, pd.DataFrame):
        iterator = errorlines.iterrows()
    elif isinstance(errorlines, pd.Series):
        iterator = errorlines.items()
    elif isinstance(errorlines, (list, tuple)):
        iterator = enumerate(errorlines)
    else:
        return ers

    for _, error in iterator:
        if isinstance(error, dict):
            ers.append(f"Bus {error['bus']} does not start or end in a garage.")
        elif isinstance(error, pd.Series):
            ers.append(f"Bus {error.get('bus')} does not start or end in a garage.")
        elif isinstance(error, bool):
            if error:
                ers.append("A bus does not start or end in a garage.")
        else:
            ers.append("A bus does not start or end in a garage.")

    return ers


print('checker: errorenums.py OK')