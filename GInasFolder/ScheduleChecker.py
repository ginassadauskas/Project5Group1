
# %% 

# the hashtag and percentage side make it a jupyter notebook cell
# that still a .py file just easier to see output 

################ - Imports

import pandas as pd 

##################
tt = pd.read_excel('Timetable.xlsx')
Dist_matrix = pd.read_excel('DistanceMatrix.xlsx')
Bus_Plan = pd.read_excel('Bus Planning.xlsx')

#  TODO might have to be changed to input from site or something here 

# order is important here for these functions to work properly

def convert_time_to_minutes(time_column: pd.Series, include_seconds: bool=True):
    '''
    Converts a column of time strings in HH:MM:SS format to minutes

    Parameters:
    ---------
    time_column : pd.Series
        A pandas Series containing time strings in HH:MM:SS format.

    Returns:
    ---------
    minutes : pd.Series
        Minutes since midnight for each time in the input column. 
    '''
    try:
        temp = pd.to_datetime(time_column, format='%H:%M:%S')
    except:
        temp = pd.to_datetime(time_column, format='%H:%M')

    minutes = temp.dt.hour * 60 + temp.dt.minute
    return minutes

def adjust_for_midnight(time_column: pd.Series, threshold: int = 180):

    '''
        Converts a column of time in minutes in int format to minutes since midnight, adjusting for times that cross midnight.

        Parameters:
        ---------
        time_column : pd.Series
            A pandas Series containing time int int format
        threshold : int
            The threshold in minutes to determine if a time is considered to be on the next day (default is 300 minutes).

        Returns:
        ---------
        pd.Series
            Adjusted minute values
    '''

    return time_column.where(time_column >= threshold, time_column + 1440)

def adjust_time(bus_plan: pd.DataFrame):
    '''Adjusts the 'start time' and 'end time' columns of a bus plan to be in minutes since midnight, accounting for times that cross midnight.

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for 'start time' and 'end time'.

    Returns:
    ---------
    pd.DataFrame
        The bus plan DataFrame with adjusted 'start time' and 'end time' columns expressed in minutes since midnight.
    '''
    bus_plan['start time'] = convert_time_to_minutes(bus_plan['start time'])
    bus_plan['end time'] = convert_time_to_minutes(bus_plan['end time'])
    bus_plan['start time'] = adjust_for_midnight(bus_plan['start time'])
    bus_plan['end time'] = adjust_for_midnight(bus_plan['end time'])

    return bus_plan

def check_for_overlaps(bus_plan:pd.DataFrame): #TODO WARNING at the bottom in the marked section 

    '''
    Checks for overlapping idle times for buses at the same location in the bus plan.

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for 'activity', 'start location', 'start time', 'end time', and 'bus'.

    Returns:
    ---------
    overlap_dict : dict
        A dict containing information about overlapping idle times, including the location, bus identifiers, and their respective start and end times.
    '''

    # filter buses by ones that are actually idle 
    # + filter out garage buses (ehvgar) since they PROBABLY have enough space to fit enough
    filtered =  bus_plan[(bus_plan['activity'] == 'idle') & (bus_plan['start location'] != 'ehvgar')]

    grouped = filtered.groupby(['start location'])
    # gives table of rows that share the same start location
    # groupby gives a tuple so it's a key and then the actual value (in this case start location)
    # this means that the key is the value of the group inside a dataframe (garage, station, etc.)

    overlap_dict = []  # make a list of possible overlaps 

    for location, group_df in grouped:
        rows = group_df.to_dict('records')  # turns the group into a plain list of dicts, one per row

        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                row_a = rows[i]
                row_b = rows[j]

                # Generate unique pairs that are not the same bus (OR5 material WOW)
                
                if row_a['bus'] == row_b['bus']:
                    continue # don't compare the same bus just in case 

                if(row_a['start time'] < row_b['end time'] and row_b['start time'] < row_a['end time']):
                    #######
                    # TODO WARNING HERE OR SOMETHING
                    print(f'Overlap at {location} at minutes {row_a['start time']} - {row_a['end time']} (BUS {row_a["bus"]}) and {row_b['start time']} - {row_b['end time']} (BUS {row_b["bus"]})')
                    #######
                    overlap_dict.append({
                    'location': location,
                    'bus_a': row_a['bus'],
                    'bus_b': row_b['bus'],
                    'start_a': row_a['start time'],
                    'end_a': row_a['end time'],
                    'start_b': row_b['start time'],
                    'end_b': row_b['end time'],
})

    return overlap_dict

def check_gaps(bus_plan: pd.DataFrame):
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

    gap_data = []  # store rows with data for warning or error 

    for bus in bus_plan['bus'].unique(): # for every unique bus number
        sorted_plan = bus_plan[bus_plan['bus'] == bus].sort_values(by='start time')
        # sort by start time 

        for i in range(1, len(sorted_plan)):
            prev_row = sorted_plan.iloc[i - 1]
            curr_row = sorted_plan.iloc[i]
            gap = curr_row['start time'] - prev_row['end time']

            if gap != 0:  # if there is a gap (positive or negative)

                gap_data.append({ # write a dict of the data that has a positive or negative time gap
                    'bus': bus,
                    'gap_time': gap, # positive if there is a genuine gap, negative if overlap
                    'prev_end_time': prev_row['end time'],
                    'curr_start_time': curr_row['start time'],
                    # CAN technically modify this so you can input what data you want from warnings 
                    # or errors and then it will just output that data in a list of dicts for you to use however you want
                })
    return gap_data

def check_start_end_location(bus_plan: pd.DataFrame): 
    
    '''
    Checks if the start location of a buses next trip matches the end location of its previous trip.

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for at least 'start location', 'end location', and 'bus'.

    Returns:
    ---------
    location_mismatches : list
        A list of dictionaries containing information about mismatches in start and end locations for each bus, including the bus identifier, previous end location, and current start location.
        also includes the start and end times to find the specific trip that has the issue.
    '''

    location_mismatches = []  # oh wow same thing as last time 

    for bus in bus_plan['bus'].unique():  # for every unique bus number
        sorted_plan = bus_plan[bus_plan['bus'] == bus].sort_values(by='start time')
        # sort by start time, technically not needed for this as with the previous one
        # just want to keep it generic 

        # general idea is that we take a bus then look at only the scedule for THAT bus


        for i in range(1, len(sorted_plan)):
            prev_row = sorted_plan.iloc[i - 1]
            curr_row = sorted_plan.iloc[i]

            # same idea as previous functions, I already mentioned this is a critical finding

            if prev_row['end location'] != curr_row['start location']:
                print(f"Location mismatch for Bus {bus}: Previous end location '{prev_row['end location']}' does not match current start location '{curr_row['start location']}'.")
                # delete print statement later and just write to a list of dicts for output to user
                # dict output looks super ugly for me rn. 
                location_mismatches.append({
                    'bus': bus,
                    'prev_end_location': prev_row['end location'],
                    'curr_start_location': curr_row['start location'],
                    'start_time': curr_row['start time'],
                    'end_time': curr_row['end time'],
                    # I think time is relevant for the client to check for issues
                })
    # verified with mismatch on rows 37 and 38 of the bus plan, so this function works as intended probably :p
    # also 18 mismatches to maybe relevant to the idling for 1 minute case 
    return location_mismatches

def check_garage(bus_plan: pd.DataFrame):
    '''
    Checks if the first and last location of the whole schedule for each bus is the garage

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for at least 'end location' 'start location' and 'bus'.

    Returns:
    ---------
    garage_issues : list
        A list of dictionaries containing information about buses with the bus identifier, the issue (whether it's first or last trip), and the location in its place
    '''

    garage_issues = []  # pretty much same with the template 

    for bus in bus_plan['bus'].unique():  # for every unique bus number
        sorted_plan = bus_plan[bus_plan['bus'] == bus].sort_values(by='start time')

        last_row = sorted_plan.iloc[-1]  # get the last trip for this bus
        first_row = sorted_plan.iloc[0] # first trip lol 


        # run two checks for the first trip and last trip 

        if first_row['start location'] != 'ehvgar':
            garage_issues.append({'bus': bus,
                                  'issue': 'does not start at garage',
                                    'start_location': first_row['start location']
                                    })
        if last_row['end location'] != 'ehvgar':
            garage_issues.append({
                'bus': bus,
                'issue': 'does not end at garage',
                'end_location': last_row['end location']
                    })

    # verified against data from the first 3 buses 

    return garage_issues

def check_line_value(bus_plan: pd.DataFrame):
        '''
    Checks that every service trip has a non-empty line value.

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for at least 'line', 'activity', 'bus' and 'start time'

    Returns:
    ---------
    line_issues : list
        A list of issues with the start time of the trip and the bus number
    '''
        line_issues = []

        filtered = bus_plan[bus_plan['activity'] == 'service trip']
        missing_line = filtered[filtered['line'].isna()] 

        for i in range(len(missing_line)):
            row = missing_line.iloc[i]
            line_issues.append(
                {
                    'bus': row['bus'],
                    'start time': row['start time'],
                }
            )

        # no such cases in the original data so can't verify but it does give like 380 values if 
        # I don't filter by service trip 
        return line_issues

def check_positive_negative_consumption(bus_plan: pd.DataFrame):
    '''

    '''
    consumption_issues = []

    for row in range(len(bus_plan)):
        if bus_plan.iloc[row]['consumption'] < 0 and bus_plan.iloc[row]['activity'] == 'charging':
            consumption_issues.append({
                'bus': bus_plan.iloc[row]['bus'],
                'start time': bus_plan.iloc[row]['start time'],
                'consumption': bus_plan.iloc[row]['consumption']
            })

        elif bus_plan.iloc[row]['consumption'] > 0 and bus_plan.iloc[row]['activity'] != 'charging':
            consumption_issues.append({
                'bus': bus_plan.iloc[row]['bus'],
                'start time': bus_plan.iloc[row]['start time'],
                'consumption': bus_plan.iloc[row]['consumption']
            })

    return consumption_issues

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

calculate_energy_levels(capacity= 300, safety_margin= 0.1, bus_plan=Bus_Plan)


# %%

# don't care about this rn 
def verify_schedule(tt, dist_matrix, bus_plan):
    '''
    Verifies the schedule based on the provided timetable, distance matrix, and bus plan.
    Writes errors or warnings and points to location if issues are found.
    '''


    return True 


# ERROR CLASSES - Emily

class BusScheduleError(Exception):
    """Base class for every error this validator can raise."""

    def __init__(self, message, row=None):
        self.row = row
        if row is not None:
            message = f"[Row {row}] {message}"
        super().__init__(message)


class InvalidFileTypeError(BusScheduleError):
    """The uploaded file isn't a .csv, .xlsx, or .xls file."""
    if Bus_Plan.suffix =! ".xlsx":
        raise ValueError(f"'{Bus_Plan.name}' is not a excel file. please insert an excel file")


class MissingColumnsError(BusScheduleError):
    """One or more required columns are missing. Uses hard values"""
    required_columns = ["start location","end location","start time","end time","activity","line","energy consumption","bus"]
    input_columns = Bus_Plan.columns
    missing_columns = set(required_columns) - set(input_columns)
    if missing_columns:
        raise IndexError(f"Unable to proceed, Missing columns: {missing_columns}, please make sure all columns are inserted")

    else:
        # now check individual columns for the data errors
        start_location = Bus_Plan["start location"]
        end_location = Bus_Plan["end location"]
        start_time = Bus_Plan["start time"]
        end_time = Bus_Plan["end time"]
        activity = Bus_Plan["activity"]
        line = Bus_Plan["line"]
        energy_consumption = Bus_Plan["energy consumption"]
        bus = Bus_Plan["bus"]

class InvalidLocationError(BusScheduleError):
    """A start/end location isn't in the allowed list."""
    allowed_locations = input("Please insert the codes of the allowed locations")
    if not all Bus_Plan['start_location'].isin(allowed_locations).all() and end_location.isin(allowed_locations).all():
                # store these invalid locations
                bad_values = file.loc[~file["status"].isin(allowed), "status"].unique()
                raise ValueError(f"Unexpected values found: {bad_values}. Are these locations correct?")
class SameLocationError(BusScheduleError):
    """Start location and end location are identical for a row."""
    start_location = Bus_Plan["start location"]
    end_location = Bus_Plan["end location"]
    for i in start_location:
        for k in end_location:
            if start_location == end_location: # check if the start location and end location is the same
                raise ValueError(f"start and end locations are the same for row # {}, is this correct?")


class InvalidActivityError(BusScheduleError):
    """An activity value isn't one of the allowed activities."""
    allowed_activities = input("please insert the allowed activities")
    activity = Bus_Plan["activity"]
    for i in activity:
        if not all activity.isin(allowed_activities).all():
            raise ValueError(f"The activities in row {i} are invalid, the activities allowed are {allowed_activities}")

class EmptyActivityError(BusScheduleError):
    """The activity field is empty."""
    activity = Bus_Plan["activity"]
    for i in activity:
        if activity.isnull():
            raise ValueError(f"Warning, row number {i} has an an empty activity")

class InvalidEnergyValueError(BusScheduleError):
    """Energy consumption isn't a valid number."""
    energy = Bus_Plan["energy consumption"]
    for idx, value in energy.items(): # if any values in the column "energy" is not a number
                is_valid = not pd.isna(pd.to_numeric(value, errors="coerce"))
                if not is_valid:
                    raise TypeError(f"Row {idx}: '{value}' is not a number or a decimal")

class InvalidIdleEnergyError(BusScheduleError):
    """An idle activity doesn't consume exactly 5 energy."""
    energy = Bus_Plan["energy consumption"]
    activity = Bus_Plan["activity"]
    for i in energy:
        for k in activity:
            if energy != 5 and activity == "idle":
                raise ValueError(f"In row # {k}, idle activites must consume 5 energy") #if the activity is idle, the energy must be equal to 5

class InvalidLineNumberError(BusScheduleError):
    """Line isn't numeric, or has more than 3 digits."""
    line = Bus_Plan["line"]
    for idx,value in line.items(): # if any values in the column line is not a number. 
        is_valid = not pd.isna(pd.to_numeric(value, errors="coerce"))
        if not is_valid:
            raise TypeError(f"Row {idx}: '{value}' is not a valid line number. Lines must be empty or have numbers with max 3 digits")
        elif len(pd.to_numeric(value, errors="coerce")) > 3:
            raise IndexError(f"Row {idx}: '{value}' is not a valid line number. It has more than 3 digits.")

class DuplicateScheduleError(BusScheduleError):
    # checks if the same line, same bus, and same start time appear at least twice.
    def check_duplicate_schedule(bus_plan: pd.DataFrame):
    
        duplicate_issues = []
        subset_cols = ['bus', 'line', 'start time']

   
        duplicates = bus_plan[bus_plan.duplicated(subset=subset_cols, keep=False)]

        for i in range(len(duplicates)):
            row = duplicates.iloc[i]
            duplicate_issues.append({
                'bus': row['bus'],
                'line': row['line'],
                'start time': row['start time'],
        })

        return ValueError(f"Duplicate bus times and lines were found, {duplicate_issues}, at rows {i}")
                
class ScheduleValidationError(BusScheduleError):
    """Aggregates every row-level error found in one validation pass."""

    def __init__(self, errors):
        self.errors = errors
        message = f"{len(errors)} validation error(s) found:\n" + "\n".join(
            f" - {e}" for e in errors
        )
        super().__init__(message)



# %%


