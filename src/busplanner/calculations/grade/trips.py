
"""Functions related to the trips taken in the current schedule
"""
import pandas as pd

def trip_time(schedule: pd.DataFrame, in_minutes: bool=False) -> pd.DataFrame:
    """Calculates how much time was spend on each trip

    [schedule] a completed bus schedule.
    [in_minues] Default False. If true, all times are represented as minutes instead of hours.
    [returns] a copy of the schudule with the times of each trip appended as a column
    """
    schedule = schedule.copy()
    if in_minutes is False:
        schedule = sc.adjust_time(schedule)

    schedule['trip duration'] = schedule['end time'] - schedule['start time']
    return schedule

def min_service_time(dd: pd.DataFrame) -> int:
     """returns the theoretical minimum trip time.

     [dd] Distance Matrix in minutes
     [returns] lowest trip time on a service trip.
     """
     return min(dd.dropna()['min_travel_time'])

def earliest_service(tt: pd.DataFrame) -> int:
     """Finds the earliest service trip
     
     [tt] Time Table in minutes
     [returns] time of first service trip"""
     return min(tt['departure_time'])

def latest_service(tt: pd.DataFrame, dd: pd.DataFrame) -> int:
     """Finds the end time of the latest service trip

     [tt] Time table in minutes
     [dd] Distance Matrix in minutes
     [returns] End time of the last bus
     """
     return max(tt['departure_time']) + max(dd.dropna()['min_travel_time'])


print('grade: trips.py OK')