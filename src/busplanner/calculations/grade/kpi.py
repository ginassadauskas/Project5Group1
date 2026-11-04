"""KPI calculations related to the current schedule
"""
from busplanner.calculations.grade import trips as t
from busplanner.calculations.imports import convert_time_to_minutes, merge_route_plan
from busplanner.calculations.power import powerpertrip
import pandas as pd


def kpi(schedule: pd.DataFrame, req_bus_line: pd.DataFrame, 
                  distance_matrix: pd.DataFrame) -> float:
    """Calculates the KPI of a given schedule.

    [schedule] A completed, verified schedule the KPI will score.
    [bus] The importance of how many buses are used compated to the minimum buses.
    [time] The importance of how much time each bus spends on non-service trips
    [battery] The importance of the battery degridation. The reduction of maximum battery capacity

    [returns] The kpi, ranging between 0 and 1.
    """
    min_bus_score = bus_ratio(schedule, req_bus_line, distance_matrix)
    battery = efficiency(schedule, merge_route_plan(req_bus_line, distance_matrix))

    # Battery only acts as a tiebreaker
    # The maximum KPI == 1.
    
    return (min_bus_score + 0.1 * battery) / 1.1

def simulbus(merged: pd.DataFrame, time: int):
     """Counts the number of buses that need to be active at the given time.
     """
     departure = convert_time_to_minutes(merged['departure_time'])
     arrival = convert_time_to_minutes(merged['arrival_time'])
     return sum(departure < time) - sum(arrival < time)

def minimum_bus(req_bus_line: pd.DataFrame, distance_matrix: pd.DataFrame) -> int:
     """Using a modified Sweep Search algorithm, find the minimum buses required.

     This function combines bus_sweep, min_b_helper, and merge_route_plan.
     These three functions are meant to be used in succession, and are only used for this function.
     """
     max_bus = 0
     merged = merge_route_plan(req_bus_line, distance_matrix)
     
     for minute in range(
         t.earliest_service(req_bus_line), 
         t.latest_service(req_bus_line, distance_matrix), 
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
     merged_energy = pd.to_numeric(merged['energy_consumption'], errors='coerce').fillna(0)
     schedule_energy = pd.to_numeric(schedule['energy consumption'], errors='coerce').fillna(0)

     merged_total = merged_energy.clip(lower=0).sum()
     schedule_total = schedule_energy.clip(lower=0).sum()

     if schedule_total == 0:
         return 0.0

     return merged_total / schedule_total

print('grade: kpi.py OK')