"""Power and energy related functions
"""
import pandas as pd

def calculate_energy_levels(capacity:int, safety_margin:float, bus_plan:pd.DataFrame, SOH: tuple=(0.85,0.95)):

    safety_margin = capacity*min(SOH)*safety_margin

    max_charge = capacity*min(SOH)

    battery_level_errors = []

    bus_plan['cum_consumption'] = bus_plan.groupby('bus')['energy consumption'].cumsum()
    bus_plan['energy_level'] = max_charge - bus_plan['cum_consumption']

    for row in range(len(bus_plan)):
        if bus_plan.iloc[row]['energy_level'] < safety_margin:
            battery_level_errors.append({
                'bus': bus_plan.iloc[row]['bus'],
                'start time': bus_plan.iloc[row]['start time'],
                'energy_level': bus_plan.iloc[row]['energy_level']
            })

    return battery_level_errors

def powerpertrip(distance_series: pd.Series):
    """Calculates how much power it takes to go from one location to another
    """
    d = distance_series.copy()

    return d*0.0016