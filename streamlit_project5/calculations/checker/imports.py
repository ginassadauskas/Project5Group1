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
