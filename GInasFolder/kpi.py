"""Functions regarding KPI calculations
"""
import pandas as pd
import ScheduleChecker as sc

SOH = (0.85, 0.95)

def calculate_kpi(schedule: pd.DataFrame, bus: int=1, time: int=1, battery: int=1) -> float:
    """Calculates the KPI of a given schedule.

    [schedule] A completed, verified schedule the KPI will score.
    [bus] The importance of how many buses are used compated to the minimum buses.
    [time] The importance of how much time each bus spends on non-service trips
    [battery] The importance of the battery degridation. The reduction of maximum battery capacity

    [returns] The kpi, ranging between 0 and 3. 3 is perfect.
    """
    return None


def minimum_bus(time_table: pd.DataFrame) -> int:
    """Calculates the minimum number of buses for a valid schedule.

    [time_table] The timetable with each required line, time and starting location.
    [returns] The minimum number of buses required.
    """

    return None

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

def trip_ratio(schedule: pd.DataFrame, trip_duration: bool | None=None) -> float:
    """Calculates the ratio of service and non-service trips.

    [schedule] The bus schedule, with or without the trip times in minutes.
    [trip time] Default None. 
        If true, the trip duration column has not been made and times are in minutes.
        If false, the the trip duration column has not been made and times are in hh:mm
        If None, the trip duration column has already been calculated
    """
    schedule = schedule.copy()

    if trip_duration is not None:
        schedule = trip_time(schedule, trip_duration)

    all_times = schedule.groupby('activity').sum()['trip duration']
    return float(1 - (all_times.sum() - all_times['service trip'])/all_times.sum())
