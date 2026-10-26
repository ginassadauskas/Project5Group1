
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