"""File mistakes that can be solved by the tool
"""
import pandas as pd
from busplanner.calculations.power import powerpertrip
from busplanner.calculations import defaults as kwh

def gaps(bus_plan: pd.DataFrame):
    '''
    Checks for gaps in the bus plan where a bus has a gap/overlap between its end time and the next start time.

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for at least 'start time', 'end time', and 'bus'.

    Returns:
    ---------
    gap_data : list
        A list of dictionaries containing information about gaps or overlaps for each bus, including the bus identifier, gap time, previous end time, and current start time.
    '''
    bus_plan = bus_plan.copy()
    bus_plan['end time'] = bus_plan.groupby('bus')['end time'].shift(1)
    bus_plan['end time'] = bus_plan['end time'].fillna(
        bus_plan['start time'].iloc[0])
    bus_plan['gap'] = bus_plan['start time'] - bus_plan['end time']
    bus_plan = bus_plan[bus_plan['gap'] != 0]
    return True if len(bus_plan) == 0 else bus_plan

def correct_consumption(bus_plan: pd.DataFrame, distance_matrix: pd.DataFrame):
    """Checks if the energy consumption matches the trip taken.
    """
    bus_plan = bus_plan.copy()
    distance_matrix = distance_matrix.copy()

    #undo line assignment
    bus_plan['line'] = bus_plan['line'].where(
        (bus_plan['activity'] == 'service trip'), None
        )

    #Service + Material trips
    distance_matrix['min battery'] = powerpertrip(
        distance_matrix['distance_m'], how='min')
    distance_matrix['max battery'] = powerpertrip(
        distance_matrix['distance_m'], how='max')
    distance_matrix = distance_matrix[
        ['start', 'end', 'line', 'min battery', 'max battery']]
    distance_matrix.rename(
        columns={'start': 'start location', 'end': 'end location'}, inplace=True)

    #Merge trips into bus plan
    bus_plan = pd.merge(bus_plan, distance_matrix, how='left', 
                        on=['start location', 'end location', 'line'])

    #Idle
    bus_plan['min battery'] = bus_plan['min battery'].where(
        (bus_plan['activity'] != 'idle'), bus_plan['duration'] * kwh.IDLE)
    bus_plan['max battery'] = bus_plan['max battery'].where(
        (bus_plan['activity'] != 'idle'), bus_plan['duration'] * kwh.IDLE)

    #Charging
    bus_plan['min battery'] = bus_plan['min battery'].where(
        (bus_plan['activity'] != 'charging'), bus_plan['duration'] * -kwh.SLOW_CHARGE)
    bus_plan['max battery'] = bus_plan['max battery'].where(
        (bus_plan['activity'] != 'charging'), bus_plan['duration'] * -kwh.FAST_CHARGE)

    incorrect_power = bus_plan.loc[
        (bus_plan['energy consumption'].abs() < bus_plan['min battery'].abs()) |
        (bus_plan['energy consumption'].abs() > bus_plan['max battery'].abs()) |
        ((bus_plan['activity'] == 'charging') & (bus_plan['energy consumption'] > 0))
    ]
    return True if len(incorrect_power) == 0 else incorrect_power

print('checker: warnings OK')