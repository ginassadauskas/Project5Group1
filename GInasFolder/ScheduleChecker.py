
# %% 

# the hashtag and percentage side make it a jupyter notebook cell
# that still a .py file just easier to see output 

################ - Imports

import pandas as pd 

##################

tt = pd.read_excel('GInasFolder/Timetable.xlsx')
Dist_matrix = pd.read_excel('GInasFolder/DistanceMatrix.xlsx')
Bus_Plan = pd.read_excel('GInasFolder/Bus Planning.xlsx')

#  TODO might have to be changed to input from site or something here 

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)

# show doctest info in output, verbose=True shows more info about the tests
# this is also needed to actually see tests that did pass 
# this only runs if the file is run directly, not if it is imported as a module

###Upon upload
def convert_empty_line_to_next(bus_plan: pd.DataFrame):
    '''
    Converts empty line values in the bus plan to the next available line value for the same bus.

    Parameters:
    ---------
    bus_plan : pd.DataFrame
        A pandas DataFrame containing the bus plan with columns for at least 'line', 'bus', and 'start time'.

    Returns:
    ---------
    bus_plan : pd.Series
        The bus plan line column with empty line values filled with the next available line value for the same bus.

    >>> test_data = pd.DataFrame({
    ...     'bus': [1, 1, 1],
    ...     'start time': [0, 10, 20],'line': [None, 401, None],
    ... })
    >>> list(convert_empty_line_to_next(test_data))
    [401.0, 401.0, -1.0]
    '''

    bus_plan = bus_plan.sort_values(by=['bus', 'start time'])
    filled = bus_plan['line'] = bus_plan.groupby('bus')['line'].bfill() 
    #bfill does exactly the thing I need in a single function

    return filled.fillna(-1)  # fill any remaining NaN values with -1 to indicate no line available


Bus_Plan['line'] = convert_empty_line_to_next(Bus_Plan)


###Upon upload
def convert_time_to_minutes(time_column: pd.Series, threshold: int=180) -> pd.Series:
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

    return _adjust_for_midnight(minutes, threshold)

##Automatically ran with prev function
def _adjust_for_midnight(time_column: pd.Series, threshold: int = 180) -> pd.Series:

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

    return bus_plan

#check step
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

                if(row_a['start time'] < row_b['end time']
                    and row_b['start time'] < row_a['end time']
                    and row_a['line'] == row_b['line']
                    and row_a['line'] != -1):

                    overlap_dict.append({
                    'location': location,
                    'bus_a': row_a['bus'],
                    'bus_b': row_b['bus'],
                    'start_a': row_a['start time'],
                    'end_a': row_a['end time'],
                    'start_b': row_b['start time'],
                    'end_b': row_b['end time'],
})
    # 18 overlaps now with the line thing
    return overlap_dict

overlaps = check_for_overlaps(Bus_Plan)

#check step
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

#check step
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


#check step
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
        if bus_plan.iloc[row]['energy consumption'] < 0 and bus_plan.iloc[row]['activity'] == 'charging':
            consumption_issues.append({
                'bus': bus_plan.iloc[row]['bus'],
                'start time': bus_plan.iloc[row]['start time'],
                'energy consumption': bus_plan.iloc[row]['energy consumption']
            })

        elif bus_plan.iloc[row]['energy consumption'] > 0 and bus_plan.iloc[row]['activity'] != 'charging':
            consumption_issues.append({
                'bus': bus_plan.iloc[row]['bus'],
                'start time': bus_plan.iloc[row]['start time'],
                'energy consumption': bus_plan.iloc[row]['energy consumption']
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


# %%

# don't care about this rn 
def verify_schedule(tt, dist_matrix, bus_plan):
    '''
    Verifies the schedule based on the provided timetable, distance matrix, and bus plan.
    Writes errors or warnings and points to location if issues are found.
    '''


    return True 
'''
These are functions to raise errors for the following:
list of errors possible:
upon inputing the file & running:
- the input is not a xlsx or a readable file
- the person stopped the program while it was running
- input file too big --Warning
- missing one of the following columns & not recoverable:
    start location	
    end location	
    start time	
    end time	
    activity	
    line	
    energy consumption	
    bus

Upon reading the file:
    -Energy consumption is 5 if idle, less than 0 if charging, greater than 0 otherwise
    -A bus can’t make two or more trips at the same time.
    -in column "activity":
        - only valid activities are: material trip, service trip, idle, charging
        - activity is blank -- warning
    - in columns "start" and "end" location:
        - must only have values of: ehvbst, ehvapt, ehvgar -- Is a station used only once? | warning
        - Start time must be before end time. Times before 3am are considered hours 25 to 28 | Not final
        - Start and end location must not be the same unless charging or idling.
    - in column "line":
        - A service trip must have a line. A non-service trips line is ignored/replaced with next service trip line.
        - bus line is empty, or (at most) 3 digits
        - if 2 buses are on the same line and idle at the same location & time for the same service trip (look 2 conditions above).
    - in column "energy consumption":
        - only floats/int
        - Energy consumption is 5 if idle, less than 0 if charging, greater than 0 otherwise
    - in column start time and end time:
        - If a start time and an end time of a trip fit wholy inside the times of another trip -- Warning
AI was used to organize classes and for simple debugging
'''
# check the file type is correct
def validate_file_type(filename: str):
    if not filename.endswith(('.xlsx', '.xls', '.csv')):
        raise InvalidFileTypeError(f"'{filename}' is not an excel/csv file. Please insert an excel or csv file.")

# check if there are any missing columns in uploaded file
def validate_columns(
    bus_plan: pd.DataFrame,
    required_columns: list
):
    missing = set(required_columns) - set(bus_plan.columns)

    if missing:
        raise MissingColumnsError(
            f"Missing columns: {missing}. "
            "Please make sure all columns are inserted."
        )
    
# check if there are any invalid locations, uses input as allowed locations.
def validate_locations(bus_plan: pd.DataFrame, allowed_locations):
    bad_start = bus_plan.loc[~bus_plan['start location'].isin(allowed_locations), 'start location']
    bad_end = bus_plan.loc[~bus_plan['end location'].isin(allowed_locations), 'end location']
    bad_values = set(bad_start.unique()) | set(bad_end.unique())
    if bad_values:
        raise InvalidLocationError(f"Unexpected location values found: {bad_values}. Are these locations correct?")
    
#check if any trips have the same start and end locations
def validate_same_location(bus_plan: pd.DataFrame):
    errors = []
    same = bus_plan[bus_plan['start location'] == bus_plan['end location']]
    for idx in same.index:
        errors.append(SameLocationError("start and end locations are the same for this row", row=idx))
    return errors

# check if there are any invalid activities
def validate_activities(bus_plan: pd.DataFrame, allowed_activities):
    bad_mask = ~bus_plan['activity'].isin(allowed_activities)
    if bad_mask.any():
        bad_values = bus_plan.loc[bad_mask, 'activity'].dropna().unique()
        raise InvalidActivityError(f"Invalid activities found: {list(bad_values)}. Allowed: {allowed_activities}")

# check if there are any activities that are empty
def validate_activity_not_empty(bus_plan: pd.DataFrame):
    empty_mask = bus_plan['activity'].isnull()
    if empty_mask.any():
        errors = [EmptyActivityError("activity field is empty", row=idx) for idx in bus_plan.index[empty_mask]]
        return errors
    return []
def validate_energy_values(bus_plan: pd.DataFrame):
    errors = []
    numeric = pd.to_numeric(bus_plan['energy consumption'], errors='coerce')
    for idx in bus_plan.index[numeric.isna()]:
        errors.append(InvalidEnergyValueError(
            f"'{bus_plan.loc[idx, 'energy consumption']}' is not a number or a decimal", row=idx))
    return errors
 
 
def validate_idle_energy(bus_plan: pd.DataFrame):
    errors = []
    idle = bus_plan[bus_plan['activity'] == 'idle']
    bad = idle[idle['energy consumption'] != 5]
    for idx in bad.index:
        errors.append(InvalidIdleEnergyError("idle activities must consume 5 energy", row=idx))
    return errors
 
 
def validate_line_numbers(bus_plan: pd.DataFrame):
    errors = []
    for idx, value in bus_plan['line'].items():
        if pd.isna(value):
            continue  # empty line is allowed
        numeric = pd.to_numeric(value, errors='coerce')
        if pd.isna(numeric):
            errors.append(InvalidLineNumberError(
                f"'{value}' is not a valid line number. Lines must be empty or numeric.", row=idx))
        elif len(str(int(numeric))) > 3:
            errors.append(InvalidLineNumberError(
                f"'{value}' has more than 3 digits.", row=idx))
    return errors
 
 
def validate_duplicate_schedule(bus_plan: pd.DataFrame):
    errors = []
    subset_cols = ['bus', 'line', 'start time']
    duplicates = bus_plan[bus_plan.duplicated(subset=subset_cols, keep=False)]
    for idx, row in duplicates.iterrows():
        errors.append(DuplicateScheduleError(
            f"Duplicate bus/line/start time combo: bus {row['bus']}, line {row['line']}, "
            f"start {row['start time']}", row=idx))
    return errors
 

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


class MissingColumnsError(BusScheduleError):
    """One or more required columns are missing. Uses hard values"""

class InvalidLocationError(BusScheduleError):
    """A start/end location isn't in the allowed list."""
   
class SameLocationError(BusScheduleError):
    """Start location and end location are identical for a row."""

class InvalidActivityError(BusScheduleError):
    """An activity value isn't one of the allowed activities."""


class EmptyActivityError(BusScheduleError):
    """The activity field is empty."""


class InvalidEnergyValueError(BusScheduleError):
    """Energy consumption isn't a valid number."""


class InvalidIdleEnergyError(BusScheduleError):
    """An idle activity doesn't consume exactly 5 energy."""


class InvalidLineNumberError(BusScheduleError):
    """Line isn't numeric, or has more than 3 digits."""


class DuplicateScheduleError(BusScheduleError):
    """There are duplicate rows"""
                
class ScheduleValidationError(BusScheduleError):
    """Aggregates every row-level error found in one validation pass."""

    def __init__(self, errors):
        self.errors = errors
        message = f"{len(errors)} validation error(s) found:\n" + "\n".join(
            f" - {e}" for e in errors
        )
        super().__init__(message)

'''
MAIN FUNCTION TO CALL TO CHECK ALL ERRORS
parameters are; the bus plan, time table, distance matrix, allowed locations, and allowed activities, and allowed columns
ai was used to help with inputing the other functions into this one and debugging syntax errors
-Emily
'''

def verify_schedule(
    filename: str,
    timetable: pd.DataFrame,
    dist_matrix: pd.DataFrame,
    bus_plan: pd.DataFrame,
    ALLOWED_ACTIVITIES: list = ["idle", "service trip", "material trip", "charging"],
    ALLOWED_LOCATIONS: list = ["ehvbst", "ehvapt", "ehvgar"],
    REQUIRED_COLUMNS: list = [
        "start location",
        "end location",
        "start time",
        "end time",
        "activity",
        "line",
        "energy consumption",
        "bus"
    ]
) -> bool:
    """
    Runs all schedule validations.

    Returns
    -------
    bool
        True if the schedule is valid, otherwise False.
    """

    errors = []

    try:
        # Fatal input checks
        validate_file_type(filename)
        validate_columns(bus_plan, REQUIRED_COLUMNS)

        # Work on a copy so that validation does not unexpectedly
        # modify the DataFrame supplied by the caller.
        bus_plan = bus_plan.copy()

        # Run validations that raise exceptions
        validate_locations(bus_plan, ALLOWED_LOCATIONS)
        validate_activities(bus_plan, ALLOWED_ACTIVITIES)

        # Run validations that return lists of errors
        errors.extend(validate_activity_not_empty(bus_plan))
        errors.extend(validate_energy_values(bus_plan))
        errors.extend(validate_idle_energy(bus_plan))
        errors.extend(validate_line_numbers(bus_plan))
        errors.extend(validate_duplicate_schedule(bus_plan))
        errors.extend(validate_same_location(bus_plan))

        # Convert times before running checks that depend on time values
        bus_plan['start time'] = convert_time_to_minutes(
            bus_plan['start time']
        )
        bus_plan['end time'] = convert_time_to_minutes(
            bus_plan['end time']
        )

        # Checks that return lists
        errors.extend(check_gaps(bus_plan))
        errors.extend(check_start_end_location(bus_plan))
        errors.extend(check_garage(bus_plan))
        errors.extend(check_line_value(bus_plan))
        errors.extend(check_positive_negative_consumption(bus_plan))
        errors.extend(check_for_overlaps(bus_plan))
    except BusScheduleError as error:
        # Fatal validation error
        errors.append(error)
    except (pd.errors.ParserError, ValueError, TypeError, KeyError) as error:
        # Unexpected problems caused by invalid data
        errors.append(
            BusScheduleError(f"Unexpected validation error: {error}")
        )
    if errors:
        return errors

    return True
# %%