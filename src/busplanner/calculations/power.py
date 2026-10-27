"""Power and energy related functions
"""
import pandas as pd
from busplanner.calculations import defaults as kwh

def safety_margin(capacity: int=kwh.MAX_SOC, soh: float=kwh.SOH, safety_margin: float=kwh.SAFETY_MARGIN):
    return capacity*max(soh)*safety_margin

def max_charge(capacity: int, soh: float):
    return capacity*min(soh)

def energy_levels(bus_plan: pd.DataFrame, 
                            capacity: int=kwh.MAX_SOC, soh: tuple=kwh.SOH, safety_margin: float=kwh.SAFETY_MARGIN):
    bus_plan = bus_plan.copy()

    bus_plan['cum_consumption'] = bus_plan.groupby('bus')['energy consumption'].cumsum()
    bus_plan['energy_level'] = max_charge(capacity, soh) - bus_plan['cum_consumption']

    return bus_plan

def powerpertrip(distance_series: pd.Series, how='avr'):
    """Calculates how much power it takes to go from one location to another
    """
    d = distance_series.copy()

    match how:
        case 'avr':
            avr = 0.5 * min(kwh.CON_PER_M) + 0.5 * max(kwh.CON_PER_M)
            return d * avr
        case 'min':
            return d * min(kwh.CON_PER_M)
        case 'max':
            return d * max(kwh.CON_PER_M)
        case _:
            return d


print('calculations: power.py OK')