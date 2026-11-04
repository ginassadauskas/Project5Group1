"""Default and configurable values.
"""

import re
import pandas as pd

"""Power variables
"""
# SOH is the estimated state of health of the buses deployed. 
#   If the SOH is None, there is no estimation, every bus has a predetermined/precalculated SOH 
SOH: tuple[float, float] | None = (0.85, 0.95)

# Safety Margin is the minimum SOC that a bus must keep before charging.
SAFETY_MARGIN: float = 0.1 #10%

# Maximum battery capacity of a bus, ignoring the buses' State of Healths.
# SOC is the current energy level, or State of Charge, in kWh.
MAX_SOC: int = 300 #kWh
# The % of starting State of Charge, taken from the max soc or equal to the SOH, if MAX_SOC * SOC > SOH. 
SOC: float = 0.9
# If False (default), the starting SOC is calculated using the SOH instead of MAX_SOC.
ABSOLUTE_SOC: bool = False 

# Idle consumption is the amount of kWh per minute a bus consumes while it is idling.
IDLE: float = 1/12 #kW

# How fast do chargers charge (per minute)?
# A bus charges at the fast charge rate while its SOC is lower than the threshold.
FAST_CHARGE: float = 7.5 #kW
SLOW_THRESHOLD: float = 0.9 #90% of the bus's SOH
# ABSOLUTE_THRESHOLD = SOH * SLOW_THRESHOLD
SLOW_CHARGE: float = 1.0 #kW

#The estimated average consumption for a bus to move 1m.
#   The estimated con per m is equal to the average of the given range
CON_PER_M: tuple[float, float] = (0.0007, 0.0025) #kW, average 0.0016 #kW

"""Import variables
"""
#At what time (in minutes) does the schedule consider it a new day.
MIDNIGHT: int = 180

"""Checker variables
"""
#A list with each charging spot.
# Common uploaded variants such as 'Garage' or 'EHV GARAGE' should map to the same canonical name.
CHARGER: list[str] = ['ehvgar']
LOCATION_ALIASES: dict[str, str] = {
    'ehvgar': 'ehvgar',
    'garage': 'ehvgar',
    'ehv garage': 'ehvgar',
    'e h v garage': 'ehvgar',
    'ehv_garage': 'ehvgar',
    'ehv-garage': 'ehvgar',
    'charging point': 'ehvgar',
    'chargingpoint': 'ehvgar',
    'garage ehv': 'ehvgar',
    'ehv garage depot': 'ehvgar',
}


COLUMN_ALIASES: dict[str, set[str]] = {
    'start time': {'start time', 'starttime', 'start_time', 'departure time', 'departure_time', 'trip start time'},
    'end time': {'end time', 'endtime', 'end_time', 'arrival time', 'arrival_time', 'trip end time'},
    'start location': {'start location', 'startlocation', 'start_location', 'from', 'from location', 'origin', 'origin location', 'departure location'},
    'end location': {'end location', 'endlocation', 'end_location', 'to', 'to location', 'destination', 'destination location', 'arrival location'},
    'activity': {'activity', 'activities', 'trip type', 'type'},
    'line': {'line', 'service line', 'route', 'route number', 'lijn', 'line number'},
    'bus': {'bus', 'vehicle', 'bus number', 'bus id', 'vehicule'},
    'energy consumption': {'energy consumption', 'energyconsumption', 'energy_consumption', 'consumption', 'energy kwh', 'kwh', 'energy (kwh)', 'consumption kwh'},
}


def normalize_column_name(value):
    """Normalize user-facing column names into the internal checker schema."""
    if value is None or value is pd.NA or pd.isna(value):
        return value

    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def resolve_column_alias(value):
    """Map common Excel header variants to the canonical internal column name."""
    text = normalize_column_name(value)
    for canonical, aliases in COLUMN_ALIASES.items():
        if text in aliases or text == canonical:
            return canonical
    return text


def normalize_bus_plan_columns(bus_plan: pd.DataFrame) -> pd.DataFrame:
    """Rename uploaded columns to the canonical checker column names."""
    if not isinstance(bus_plan, pd.DataFrame):
        return bus_plan

    normalized = bus_plan.copy()
    rename_map = {}
    used_targets = set()

    for column in list(normalized.columns):
        canonical = resolve_column_alias(column)
        if canonical in used_targets:
            continue
        if canonical in normalized.columns and canonical != column:
            continue
        if canonical != column:
            rename_map[column] = canonical
            used_targets.add(canonical)

    if rename_map:
        normalized = normalized.rename(columns=rename_map)

    return normalized


def normalize_location_name(value):
    """Normalize location names and accept common aliases used in uploaded schedules."""
    if value is None or value is pd.NA or pd.isna(value):
        return value

    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(' e h v ', ' ehv ')
    text = re.sub(r"\s+", " ", text).strip()
    return LOCATION_ALIASES.get(text, text)


#A set of the required columns
REQ_COL: set[str] = set(
    [
        'start location', 
        'end location', 
        'start time', 
        'end time', 
        'activity', 
        'line', 
        'bus',
        'energy consumption'
    ]
)

#Energy consumption is optional, as our tool can automatically calculate it before verifying.

ACTIVITIES: set[str] = set(['service trip', 'material trip', 'charging', 'idle'])


print('calculations: defaults.py OK')