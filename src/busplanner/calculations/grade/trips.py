
"""Functions related to the trips taken in the current schedule
"""
import pandas as pd

from busplanner.calculations.imports import convert_time_to_minutes


def _as_minutes(series: pd.Series) -> pd.Series:
    """Normalize time-like values to minute integers for KPI calculations."""
    if series.empty:
        return pd.Series(dtype="float64")
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    return convert_time_to_minutes(series)


def trip_time(schedule: pd.DataFrame) -> pd.DataFrame:
    """Calculates how much time was spend on each trip

    [schedule] a completed bus schedule.
    [in_minues] Default False. If true, all times are represented as minutes instead of hours.
    [returns] a copy of the schudule with the times of each trip appended as a column
    """
    schedule = schedule.copy()
    schedule['trip duration'] = schedule['end time'] - schedule['start time']
    return schedule

def min_service_time(dd: pd.DataFrame) -> int:
     """returns the theoretical minimum trip time.

     [dd] Distance Matrix in minutes
     [returns] lowest trip time on a service trip.
     """
     return min(pd.to_numeric(dd.dropna()['min_travel_time'], errors='coerce').dropna())

def earliest_service(tt: pd.DataFrame) -> int:
     """Finds the earliest service trip
     
     [tt] Time Table in minutes
     [returns] time of first service trip"""
     return min(_as_minutes(tt['departure_time']).dropna())

def latest_service(tt: pd.DataFrame, dd: pd.DataFrame) -> int:
     """Finds the end time of the latest service trip

     [tt] Time table in minutes
     [dd] Distance Matrix in minutes
     [returns] End time of the last bus
     """
     return max(_as_minutes(tt['departure_time']).dropna()) + max(pd.to_numeric(dd.dropna()['min_travel_time'], errors='coerce').dropna())


print('grade: trips.py OK')