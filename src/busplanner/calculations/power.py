"""Power and energy related functions
"""
import pandas as pd
from . import defaults as kwh

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

def powerpertrip(distance_series: pd.Series):
    """Calculates how much power it takes to go from one location to another
    """
    d = distance_series.copy()

    return d*kwh.CON_PER_M


print('calculations: power.py OK')