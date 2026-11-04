"""KPI calculations related to the current schedule
"""
from busplanner.calculations.grade import trips as t
from busplanner.calculations.imports import merge_route_plan, normalize_schedule_values
from busplanner.calculations.power import powerpertrip
import pandas as pd


def _prepare_schedule_for_kpi(schedule: pd.DataFrame) -> pd.DataFrame:
    """Normalize schedule columns used in KPI calculations to numeric values."""
    return normalize_schedule_values(schedule)


def kpi(schedule: pd.DataFrame, req_bus_line: pd.DataFrame, 
                  distance_matrix: pd.DataFrame) -> float:
    """Calculates the KPI of a given schedule.

    [schedule] A completed, verified schedule the KPI will score.
    [bus] The importance of how many buses are used compated to the minimum buses.
    [time] The importance of how much time each bus spends on non-service trips
    [battery] The importance of the battery degridation. The reduction of maximum battery capacity

    [returns] The kpi, ranging between 0 and 1.
    """
    normalized_schedule = _prepare_schedule_for_kpi(schedule)
    normalized_req = _prepare_schedule_for_kpi(req_bus_line)

    min_bus_score = bus_ratio(normalized_schedule, normalized_req, distance_matrix)
    battery = efficiency(normalized_schedule, merge_route_plan(normalized_req, distance_matrix))

    # Battery only acts as a tiebreaker
    # The maximum KPI == 1.
    
    return (min_bus_score + 0.1 * battery) / 1.1

def simulbus(merged: pd.DataFrame, time: int):
     """Counts the number of buses that need to be active at the given time.
     """
     merged = _prepare_schedule_for_kpi(merged)
     return sum(merged['departure_time'] < time) - sum(merged['arrival_time'] < time)

def minimum_bus(req_bus_line: pd.DataFrame, distance_matrix: pd.DataFrame) -> int:
     """Using a modified Sweep Search algorithm, find the minimum buses required.

     This function combines bus_sweep, min_b_helper, and merge_route_plan.
     These three functions are meant to be used in succession, and are only used for this function.
     """
     max_bus = 0
     normalized_req = _prepare_schedule_for_kpi(req_bus_line)
     merged = merge_route_plan(normalized_req, distance_matrix)
     
     for minute in range(
         t.earliest_service(normalized_req), 
         t.latest_service(normalized_req, distance_matrix), 
         t.min_service_time(distance_matrix)
     ):  
        
        bus_need = simulbus(merged, minute)
        max_bus = bus_need if bus_need > max_bus else max_bus

     return max_bus

def count_buses(schedule: pd.DataFrame) -> int:
     """Counts the number of buses used in the given schedule.

     [schedule] The schedule of which the KPI needs to be calculated.
     [returns] The number of buses used.
     """
     return len(schedule['bus'].unique())

def bus_ratio(schedule: pd.DataFrame, req_bus_line: pd.DataFrame, distance_matrix: pd.DataFrame) -> float:
     """Calculates the ratio between number of buses used and minimum buses required.

    [schedule] The schedule of which the KPI needs to be calculated.
    [req_bus_line] a dataframe containing each bus line that is run through the day.
    [distance_matrix] a dataframe containing the distance and length of each trip.

    [return] the ratio, ranging between 0 to 1.
     """
     return count_buses(schedule) / minimum_bus(req_bus_line, distance_matrix)

def efficiency(schedule: pd.DataFrame, merged: pd.DataFrame):
     # clip sets all negative values to 0, removing capacity gained from charging.
     # Therefor, we onlly include (theoretical minimum) the energy consumed.
     merged = _prepare_schedule_for_kpi(merged)
     schedule = _prepare_schedule_for_kpi(schedule)

     merged_energy_col = "energy_consumption" if "energy_consumption" in merged.columns else "energy consumption"
     schedule_energy_col = "energy_consumption" if "energy_consumption" in schedule.columns else "energy consumption"

     merged_energy = merged.get(merged_energy_col)
     if merged_energy is None:
         merged_energy = pd.Series(0, index=merged.index)
     else:
         merged_energy = pd.to_numeric(merged_energy, errors='coerce').fillna(0)

     schedule_energy = schedule.get(schedule_energy_col)
     if schedule_energy is None:
         schedule_energy = pd.Series(0, index=schedule.index)
     else:
         schedule_energy = pd.to_numeric(schedule_energy, errors='coerce').fillna(0)

     merged_total = float(merged_energy.clip(lower=0).sum())
     schedule_total = float(schedule_energy.clip(lower=0).sum())

     if schedule_total == 0:
         return 0.0

     return merged_total / schedule_total

print('grade: kpi.py OK')