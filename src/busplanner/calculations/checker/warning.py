"""File mistakes that can be solved by the tool
"""
import pandas as pd
from busplanner.calculations.power import powerpertrip
from busplanner.calculations import defaults as kwh
from busplanner.calculations.imports import cmh

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

    bus_plan['duration'] = bus_plan['end time'] - bus_plan['start time']

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

    if len(incorrect_power) == 0:
        return True

    fixed = bus_plan.copy()
    fixed['energy consumption'] = fixed['energy consumption'].where(
        ~fixed.isin(incorrect_power)['energy consumption'], #Leave all accepted values as is
        (fixed['max battery'] + fixed['min battery']) / 2 #Change incorrect values to the average of the accepted range.
        )

    return warning_correct_consumption(incorrect_power), fixed

def warning_correct_consumption(errorlines: pd.DataFrame):
    ers = []

    for _, error in errorlines.iterrows():
        ers.append(f'''The bus activity starting at {cmh(error['start time'])} has an incorrect consumption of {error['energy consumption']}. \n
                   Allowed range is between {error['min battery']} and {error['max battery']} and has been corrected to the average of the two.''')

    return ers

print('checker: warnings OK')