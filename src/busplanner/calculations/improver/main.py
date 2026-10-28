### IMPORTS
from busplanner.calculations.grade import kpi 
from busplanner.calculations.imports import convert_time_to_minutes
from busplanner.calculations.imports import merge_route_plan
import math
import pandas as pd


# TEMP # TODO read from data inside the site 

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "GInasFolder"

# TEMP 

###

### CONSTANTS ###

from busplanner.calculations import defaults as d
from busplanner.calculations.power import safety_margin, max_charge

GARAGE = d.CHARGER[0]
CHARGE_RATE = d.FAST_CHARGE
IDLE_RATE = d.IDLE                                   # kWh per minute
KWH_PER_KM = 1000 * sum(d.CON_PER_M) / 2      
Q = max_charge(d.MAX_SOC, d.SOH)                    
S_MIN = safety_margin(d.MAX_SOC, d.SOH, d.SAFETY_MARGIN)  
TARGET = d.SLOW_THRESHOLD * Q                       

###           ###

def load_trips(timetable, distance_matrix):
    trips = merge_route_plan(timetable, distance_matrix)
    travel = distance_matrix[['start', 'end', 'line', 'max_travel_time']]
    trips = trips.drop(columns='arrival_time').merge(travel, on=['start', 'end', 'line'], how='left')
    trips['arrival_time'] = trips['departure_time'] + trips['max_travel_time']
    trips['energy'] = trips['energy_consumption']
    trips.sort_values(by='departure_time', inplace=True)
    trips.reset_index(drop=True, inplace=True)
    return trips

tt = pd.read_excel(DATA / "Timetable.xlsx")
dm = pd.read_excel(DATA / "DistanceMatrix.xlsx")

trips = load_trips(tt,dm)
remaining_service = trips.to_dict('records')

def load_deadhead(dm):
    """
    Load the deadhead travel time and energy consumption between all pairs of locations from the distance matrix.

    :Output:
    - dh: a dictionary with keys (start, end) and values (drive_min, drive_kwh)
    """
    non_service = dm[dm['line'].isna()]
    dh = {}
    for row in non_service.itertuples():
        key = (row.start, row.end)
        value = (row.max_travel_time, row.distance_m/1000 * KWH_PER_KM)
        dh[key] = value
    return dh

def deadhead(dh, start, end):
    """
    Lookup the deadhead travel time and energy consumption between two locations.

    :Output:
    - drive_min: the deadhead travel time in minutes
    - drive_kwh: the deadhead energy consumption in kWh
    """
    if start == end:
        return (0, 0.0)          # already there: no minutes, no energy
    return dh[(start, end)]

dh = load_deadhead(dm) #deadhead lookup 

def find_next_trip(remaining,dh, loc, t, charge): 
    '''
    find the next trip that can be assigned to a bus based on its current location, time, and charge level.
    
    :Input:
    - remaining: list of trips that have not been assigned to a bus yet
    - dh: deadhead lookup table
    - loc: current location of the bus
    - t: current time in minutes for the bus
    - charge: current charge in kWh for the bus
    :Output:
    - trip: the next trip that can be assigned to the bus, or None if no trip can be assigned
    - status: a string indicating the reason why no trip can be assigned ("ok", "low battery", or "no_trips")

    '''

    # remaining = trips that have not been assigned to a bus yet
    # dh = deadhead lookup table
    # loc = current location of the bus
    # t = current time in minutes for the bus
    # charge = current charge in kWh for the bus

    time_ok = False

    for trip in remaining:

        

        drive_min, drive_kwh = deadhead(dh, loc, trip['start']) #lookup values

        if t + drive_min > trip['departure_time']:
            continue

        time_ok = True

        # charge calculations

        idle_kwh = IDLE_RATE * (trip['departure_time'] - (t + drive_min))

        home_kwh = deadhead(dh, trip['end'], GARAGE)[1] # from trip end to garage, only return kWh

        left = charge - drive_kwh - idle_kwh - home_kwh - trip['energy'] 
        # en
        if left < S_MIN:
            continue

        return trip, "ok"
    return None, "low battery" if time_ok else "no_trips"

def assign_trip(trip, dh, loc, t, charge, rows, bus):
    ''''''
    drive_min, drive_kwh = deadhead(dh, loc, trip['start'])

    # MATERIAL CASE
    if drive_min > 0:
        rows.append({
            
            'start location': loc,
            'end location': trip['start'],
            'start time': t,
            'end time': t + drive_min,
            'activity': 'material',
            'line': None,
            'energy consumption': -drive_kwh,
            'bus': bus,
        })
        t += drive_min
        charge -= drive_kwh
        loc = trip['start']


        # IDLE CASE
    if t < trip['departure_time']:
        idle_kwh = IDLE_RATE * (trip['departure_time'] - t)
        rows.append({
            'start location': loc,
            'end location': loc,
            'start time': t,
            'end time': trip['departure_time'],
            'activity': 'idle',
            'line': None,
            'energy consumption': -idle_kwh,
            'bus': bus,
        })
        t = trip['departure_time']
        charge -= idle_kwh

    # SERVICE CASE(always happens)
        
    rows.append({
        'start location': trip['start'],
        'end location': trip['end'],
        'start time': trip['departure_time'],
        'end time': trip['arrival_time'],
        'activity': 'service',
        'line': trip['line'],
        'energy consumption': -trip['energy'],
        'bus': bus,
    })

    loc = trip['end']
    t = trip['arrival_time']
    charge -= trip['energy']
    return loc, t, charge

    #####

    # Change parameters of the bus based on what it did 
    
def charge_bus(t, charge, target, rate, rows, bus):
    '''
    Charge the bus at the garage until it reaches the target charge level.
    Helper function.
    '''
    if charge < target:

        charge_needed = target - charge
        time_needed = math.ceil(charge_needed / rate)

        
        rows.append({
            'start location': GARAGE,
            'end location': GARAGE,
            'start time': t,
            'end time': t + time_needed,
            'activity': 'charging',
            'line': None,
            'energy consumption': time_needed * rate,
            'bus': bus,
        })

        t += time_needed
        charge += time_needed * rate
    return t, charge
    
def go_home(dh, loc, t, charge, rows, bus):
    '''
    Assign a deadhead trip to the bus for when it has to drive back to the station.
    Helper function.
    '''
    drive_min, drive_kwh = deadhead(dh, loc, GARAGE)
    if drive_min > 0:
        rows.append({
            'start location': loc,
            'end location': GARAGE,
            'start time': t,
            'end time': t + drive_min,
            'activity': 'material',
            'line': None,
            'energy consumption': -drive_kwh,
            'bus': bus,
        })
        t += drive_min
        charge -= drive_kwh
        loc = GARAGE
    return loc, t, charge

def build_bus(bus, remaining):
    """
    Build a schedule for a single bus based on the remaining trips and the deadhead lookup table. With all the 
    constraints in mind
    """

    # INIT
    loc, t, charge = GARAGE, 0, Q
    rows = []


    while True:
        trip, status = find_next_trip(remaining, dh, loc, t, charge)

        if status == "ok":
            loc, t, charge = assign_trip(trip, dh, loc, t, charge, rows, bus)
            remaining.remove(trip) 
            # trip is filled, remove it from list of ones that need to be completed
        elif status == "no_trips": # no trips left to assign, go home and break the loop
            loc, t, charge = go_home(dh, loc, t, charge, rows, bus) 
            break
        else:  # low_battery
            loc, t, charge = go_home(dh, loc, t, charge, rows, bus)
            if loc == GARAGE and charge >= TARGET: # prevent infinite loop if bus is already at garage and has enough charge
                break
            t, charge = charge_bus(t, charge, TARGET, CHARGE_RATE, rows, bus)
    return rows

def build_schedule(remaining):
    """
    Build a schedule for all buses based on the remaining trips and the deadhead lookup table.
    """
    all_rows = []
    bus = 1 # must be at least 1 bus 
    while remaining: # if there are still trips left to assign, keep building buses
        rows = build_bus(bus, remaining)
        if not rows:
            break
        all_rows.extend(rows) # extend the list of all rows with the rows for the current bus that are possible
        bus += 1
    return pd.DataFrame(all_rows)

    remaining_service = trips.to_dict('records')


# BUILD THE ACTUAL SCHEDULE
built_schedule = build_schedule(remaining_service)


# below is the final dataframe here that can actually be integrated

df_schedule = pd.DataFrame(built_schedule)
df_schedule['energy consumption'] = -df_schedule['energy consumption']


### 

## AI USAGE ##

# Explaining the ideas behind the heuristic (trip feasibility, battery reserve, charging at the garage).
# Reviewing code I wrote and pointing out bugs.
# Short example snippets, which I adapted myself.
# Troubleshooting file path issues
# refactoring the code to work with the new file structure


##

