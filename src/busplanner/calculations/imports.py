"""All functions related to importing the files
"""
import pandas as pd
from .defaults import MIDNIGHT
from .power import powerpertrip

def convert_time_to_minutes(time_column: pd.Series, threshold: int=MIDNIGHT) -> pd.Series:
    '''
    Converts a column of time strings in HH:MM:SS format to minutes

    Parameters:
    ---------
    time_column : pd.Series
        A pandas Series containing time strings in HH:MM:SS format.

    Returns:
    ---------
    minutes : pd.Series
        Minutes since midnight for each time in the input column. 
    '''
    try:
        temp = pd.to_datetime(time_column, format='%H:%M:%S')
    except:
        temp = pd.to_datetime(time_column, format='%H:%M')

    minutes = temp.dt.hour * 60 + temp.dt.minute
    return _adjust_for_midnight(minutes, threshold)

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

def merge_route_plan(timetable: pd.DataFrame, distance_matrix: pd.DataFrame) -> pd.DataFrame:
    """Merges the excel lines that need to be run and the distance file of those lines.

    [req_bus_line] a dataframe containing each bus line that is run through the day.
    [distance_matrix] a dataframe containing the distance and length of each trip.

    [returns] the merged file.
    """
    timetable = timetable.copy()
    distance = distance_matrix.copy()["start", "end", "line"]
    distance["energy_consumption"] = powerpertrip(distance_matrix["distance_m"])

    timetable = timetable.merge(
        distance,
        on=["start", "end", "line"],
        how="left"
    )

    timetable["departure_time"] = convert_time_to_minutes(timetable["departure_time"])
    timetable['arrival_time'] = timetable['departure_time']+distance_matrix['max_travel_time']    

    return timetable
