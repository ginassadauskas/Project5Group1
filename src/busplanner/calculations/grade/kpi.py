"""KPI calculations related to the current schedule
"""
def kpi(schedule: pd.DataFrame, req_bus_line: pd.DataFrame, 
                  distance_matrix: pd.DataFrame, bus: int=1, time: int=1,
                  in_minutes: bool | None=False) -> float:
    """Calculates the KPI of a given schedule.

    [schedule] A completed, verified schedule the KPI will score.
    [bus] The importance of how many buses are used compated to the minimum buses.
    [time] The importance of how much time each bus spends on non-service trips
    [battery] The importance of the battery degridation. The reduction of maximum battery capacity

    [returns] The kpi, ranging between 0 and 1.
    """
    #if time_table2 is not None:
    #    time_table == merge_timedistance(time_table, time_table2)

    min_bus_score = bus*bus_ratio(schedule, req_bus_line, distance_matrix)
    battery = time*trip_ratio(schedule, trip_duration=in_minutes)

    return min_bus_score + battery


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


def simulbus(merged: pd.DataFrame, time: int):
     """Counts the number of buses that need to be active at the given time.
     """
     return sum(merged['departure_time'] < time) - sum(merged['arrival_time'] < time)

def minimum_bus(req_bus_line: pd.DataFrame, distance_matrix: pd.DataFrame) -> int:
     """Using a modified Sweep Search algorithm, find the minimum buses required.

     This function combines bus_sweep, min_b_helper, and merge_route_plan.
     These three functions are meant to be used in succession, and are only used for this function.
     """
     max_bus = 0
     merged = merge_route_plan(req_bus_line, distance_matrix)
     
     for minute in range(
         earliest_service(req_bus_line), 
         latest_service(req_bus_line, distance_matrix), 
         min_service_time(distance_matrix)
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


print('grade: kpi.py OK')