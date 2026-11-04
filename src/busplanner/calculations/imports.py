"""All functions related to importing the files
"""
import re

import pandas as pd
from .defaults import MIDNIGHT
from .power import powerpertrip

def find_bustrip(incomplete: pd.DataFrame, original: pd.DataFrame, drop: bool=False):
    """Finds the original dataframe from an incomplete subset.

    This function is used when returning the original trip after processing.

    [incomplete] A subset of a modified dataframe. 
        It should contain only the neccessary rows and the unmodified columns.

    [original] Is the complete trip database with only import processing.

    [returns] The original version of the trips requested with [incompltete].

    -Modified code. Original by jakevdp & alpha_989
    https://stackoverflow.com/questions/33282119/pandas-filter-dataframe-by-another-dataframe-by-row-elements
    """
    keys = list(incomplete.columns.values)
    i1 = original.set_index(keys).index
    i2 = incomplete.set_index(keys).index
    
    if drop:
        return original[i1.isin(i2)].reset_index(drop=drop)
    else:
        return original[i1.isin(i2)]

def convert_time_to_minutes(time_column: pd.Series, threshold: int=MIDNIGHT) -> pd.Series:
    '''
    Converts a column of time strings in HH:MM:SS format to minutes.

    This also accepts numeric values that are already stored as minutes since midnight,
    so the same function can safely be reused after earlier normalization.
    '''
    if time_column is None or len(time_column) == 0:
        return time_column

    if pd.api.types.is_numeric_dtype(time_column):
        minutes = pd.to_numeric(time_column, errors='coerce')
        return _adjust_for_midnight(minutes, threshold)

    if pd.api.types.is_datetime64_any_dtype(time_column):
        minutes = time_column.dt.hour * 60 + time_column.dt.minute
        return _adjust_for_midnight(minutes, threshold)

    normalized_minutes = []
    for value in time_column:
        if pd.isna(value):
            normalized_minutes.append(float('nan'))
            continue

        if isinstance(value, (int, float)):
            normalized_minutes.append(float(value))
            continue

        text = str(value).strip()
        if re.fullmatch(r"\d+", text):
            normalized_minutes.append(float(text))
            continue

        parsed = pd.to_datetime(text, errors='coerce')
        if pd.isna(parsed):
            raise ValueError(f"Could not parse time value: {value!r}")
        normalized_minutes.append(parsed.hour * 60 + parsed.minute)

    minutes = pd.Series(normalized_minutes, index=time_column.index)
    return _adjust_for_midnight(minutes, threshold)

def convert_minutes_to_time(time_column: pd.Series):
    """Converts a pd.Series from minutes back to time.

    Credit-"user3483203"
    https://stackoverflow.com/questions/51565978/converting-a-column-of-minutes-to-hours-and-minutes-in-python
    """
    return pd.to_datetime(time_column, unit='m').dt.strftime('%H:%M')

def _adjust_for_midnight(time_column: pd.Series, threshold: int=MIDNIGHT) -> pd.Series:

    '''
        Converts a column of time in minutes in int format to minutes since midnight, adjusting for times that cross midnight.

        Parameters:
        ---------
        time_column : pd.Series
            A pandas Series containing time int int format
        threshold : int
            The threshold in minutes to determine if a time is considered to be on the next day (default is 300 minutes).

        Returns:
        ---------
        pd.Series
            Adjusted minute values
    '''

    return time_column.where(time_column >= threshold, time_column + 1440)

def normalize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize common imported column names so Excel files and project internals match."""
    if df is None or not isinstance(df, pd.DataFrame):
        return df

    normalized = df.copy()
    renamed = {}

    for column in list(normalized.columns):
        key = str(column).strip().lower().replace(" ", "_").replace("-", "_")
        key = key.replace("(", "").replace(")", "").replace("%", "")
        key = key.replace("_+", "_")

        mapping = {
            "start_location": "start",
            "start": "start",
            "end_location": "end",
            "end": "end",
            "line_id": "line",
            "line": "line",
            "distance_m": "distance_m",
            "distance": "distance_m",
            "max_travel_time": "max_travel_time",
            "max_travel_time_min": "max_travel_time",
            "min_travel_time": "min_travel_time",
            "departure_time": "departure_time",
            "departure": "departure_time",
            "arrival_time": "arrival_time",
            "arrival": "arrival_time",
            "energy_consumption": "energy_consumption",
            "energy_consumption_kwh": "energy_consumption",
            "energy_consumption_wh": "energy_consumption",
            "energy_consumption_": "energy_consumption",
            "energy_consumption_total": "energy_consumption",
            "energy_consumption_in_kwh": "energy_consumption",
            "energy_consumption_kwh_": "energy_consumption",
            "energy_consumption_per_trip": "energy_consumption",
            "energy_consumption_value": "energy_consumption",
            "energy_consumption_value_kwh": "energy_consumption",
            "energy_consumption_value_": "energy_consumption",
            "start_time": "start_time",
            "end_time": "end_time",
            "starttime": "start_time",
            "endtime": "end_time",
        }

        canonical = mapping.get(key, key)
        if canonical != key:
            renamed[column] = canonical

    return normalized.rename(columns=renamed)


def normalize_schedule_values(df: pd.DataFrame, rename_columns: bool = False) -> pd.DataFrame:
    """Normalize numeric/time values without altering the original bus-schedule column names by default."""
    if df is None or not isinstance(df, pd.DataFrame):
        return df

    normalized = normalize_dataframe_columns(df) if rename_columns else df.copy()

    for column in ["start time", "start_time", "end time", "end_time", "departure_time", "arrival_time"]:
        if column in normalized.columns:
            normalized[column] = convert_time_to_minutes(normalized[column])

    for column in [
        "energy consumption",
        "energy_consumption",
        "min_travel_time",
        "max_travel_time",
        "distance_m",
    ]:
        if column in normalized.columns:
            normalized[column] = pd.to_numeric(normalized[column], errors='coerce')

    return normalized


def merge_route_plan(timetable: pd.DataFrame, distance_matrix: pd.DataFrame) -> pd.DataFrame:
    """Merges the excel lines that need to be run and the distance file of those lines.

    [req_bus_line] a dataframe containing each bus line that is run through the day.
    [distance_matrix] a dataframe containing the distance and length of each trip.

    [returns] the merged file.
    """
    timetable = timetable.copy()
    distance = distance_matrix.copy()[["start", "end", "line", "max_travel_time"]]  
    distance["energy_consumption"] = powerpertrip(distance_matrix["distance_m"])

    timetable = timetable.merge(
        distance,
        on=["start", "end", "line"],
        how="left"
    )

    timetable["departure_time"] = convert_time_to_minutes(timetable["departure_time"])
    timetable['arrival_time'] = timetable['departure_time'] + timetable['max_travel_time']   # edit: distance_matrix -> timetable
    timetable = timetable.drop(columns='max_travel_time')      
    return timetable


print('calculations: imports.py OK')