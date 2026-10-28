"""File mistakes that can be solved by the tool
"""
import pandas as pd
from busplanner.calculations.power import powerpertrip
from busplanner.calculations import defaults as kwh

def start_garage(bus_plan: pd.DataFrame) -> pd.DataFrame | bool:
    '''
    Checks if the first and last location of the whole schedule for each bus is the garage

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for at least 'end location' 'start location' and 'bus'.

    Returns:
    ---------
    garage_issues : pd.DataFrame
        Each entry with a bus that has a starting or ending location not in an available garage.
    '''

    garage_issues = []  # pretty much same with the template 

    for bus in bus_plan['bus'].unique():  # for every unique bus number
        sorted_plan = bus_plan[bus_plan['bus'] == bus].sort_values(by='start time')
        first_row = sorted_plan.iloc[0]
        last_row = sorted_plan.iloc[-1]

        if first_row['start location'] not in kwh.CHARGER:
            garage_issues.append(first_row)
        if last_row['end location'] not in kwh.CHARGER:
            garage_issues.append(last_row)

    # verified against data from the first 3 buses 

    if len(garage_issues) == 0:
        return True
    return pd.concat(garage_issues)

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