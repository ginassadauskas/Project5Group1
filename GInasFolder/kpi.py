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

def minute_ratio(schedule: pd.DataFrame, in_minutes: bool=False) -> float:
    """Calculates how much time was spend on non-serive trips

    [schedule] a completed bus schedule.
    [in_minues] Default False. If true, all times are represented as minutes.
    [returns] a ratio of total time to time spend on non-service trips
    """
    if in_minutes is False:
        schedule['start time'] = sc.
