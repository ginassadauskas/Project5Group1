"""All functions related to importing the files
"""
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
        try:
            temp = pd.to_datetime(time_column, format='%H:%M')
        except:
            return time_column

    minutes = temp.dt.hour * 60 + temp.dt.minute
    return _adjust_for_midnight(minutes, threshold)

def cmh(minutes: int):
    """Converts a single time into HH:MM
    """
    HH = str(int(minutes) // 60)
    MM = str(int(minutes) % 60)
    if len(HH) == 1:
        HH = '0' + HH
    if len(MM) == 1:
        MM = '0' + MM
    return f"{HH}:{MM}"

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