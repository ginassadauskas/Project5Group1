"""Functions regarding KPI calculations
"""
import pandas as pd

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
