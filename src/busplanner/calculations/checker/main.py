from itertools import compress
from typing import Any
import pandas as pd
import streamlit as st
from busplanner.calculations.checker import errors as e
from busplanner.calculations.checker import warning as w
from busplanner.calculations.checker import errorenums as ee
from busplanner.calculations.checker.imports import import_bus_plan


def _has_issue(result):
    """Normalize a checker result into a plain boolean."""
    if result is True:
        return False
    if result is False:
        return True
    if result is None:
        return False
    if isinstance(result, (pd.Series, pd.DataFrame, list, tuple, set, dict, str)):
        return len(result) > 0
    try:
        return bool(result)
    except (TypeError, ValueError):
        return False


def import_checks(filepath: str) -> tuple[bool, pd.DataFrame | str]:
    """imports and verifies the state of the bus_plan.

    [returns] 
        True, bus_plan if no errors were encountered
        False, errors if an import error was encountered.
    """
    if e.validate_file_type(filepath) == True:
        bus_plan = pd.read_excel(filepath)
        missing_bus_plan_columns = e.validate_columns(bus_plan)
        if missing_bus_plan_columns == True:
            bus_plan = import_bus_plan(bus_plan)
        else: 
            return (False, missing_bus_plan_columns)
    else:
        return (False, filepath)

def verify_bus(bus_plan: pd.DataFrame):
    """Checks for any mistakes in the bus_plan

    When this function runs, each entry must already be fully imported.

    [returns] True if there are no errors else it returns a list containing 2 tuples.
        A list with tuples and errors.
        The tuple acts as an indicator which errors have been found.
            The first represents missing activities.
            The second represents unknown activities.
            The third represents missing lines on service trips.
            The fourth represents inconsistent bus/trip times.
            The fifth represents inconsistant bus locations.
    -Cretid for compress: Ashwini Chaudhary
    https://stackoverflow.com/questions/18665873/filtering-a-list-based-on-a-list-of-booleans
    """
    checks = [
        e.activity_none_empty(bus_plan),
        e.validate_activities(bus_plan),
        e.service_line(bus_plan),
        e.gaps(bus_plan),
        e.bus_teleport(bus_plan)
    ]
    errors = [_has_issue(error) for error in checks]

    if not any(errors):
        return True

    return [check for check, has_error in zip(checks, errors) if has_error]

def verify_critical(bus_plan: pd.DataFrame, 
                    distance_matrix: pd.DataFrame, 
                    merged: pd.DataFrame) -> list[Any] | bool:
    """Verifies all errors that can be dirived from the timetable or distance matrix. 

    When this function runs, each entry must already be fully imported.

    [returns] True if there are no errors else it returns a list containing 2 tuples.
        A list with tuples and errors.
        The tuple acts as an indicator which errors have been found.
            The first represents missing required service trips.
            The second represents unknown locations.
            The third represents unknown lines.
    """
    checks = [
        e.all_service_ran(bus_plan, merged),
        e.validate_locations(bus_plan, distance_matrix),
        e.validate_line_numbers(bus_plan, distance_matrix)
    ]
    errors = [_has_issue(error) for error in checks]

    if not any(errors):
        return True

    return [check for check, has_error in zip(checks, errors) if has_error]

def verify_schedule(bus_plan_file: str | pd.DataFrame) -> list[Any] | bool:
    """Verifies the full bus_plan.

    The function expects the bus planning file or DataFrame to be validated.
    """

    # def verifyschedule(schedule, mergedtable):
    #    import_checks
    #       Return if failure else continue
    #    verify_bus
    #       Return if failure else continue
    #    verify_critical
    #       Return if failure else continue
    #    correct_consumption| warning
    #       input(Fix?) if failure else continue
    #    validate_energy    | e.validate_energy(bus_plan)
    #       Return if failure else continue
    #    Warning.py         | warning
    #       input(Fix?) if failure else continue

    if isinstance(bus_plan_file, pd.DataFrame):
        bus_plan = bus_plan_file
    else:
        import_result = import_checks(bus_plan_file)
        if not isinstance(import_result, tuple) or len(import_result) != 2:
            return False
        if import_result[0] is False:
            return import_result[1],
        bus_plan = import_result[1]

    bus_result = verify_bus(bus_plan)
    if bus_result is not True:
        return bus_result,

    if hasattr(e, "validate_energy") and callable(e.validate_energy):
        energy_result = e.validate_energy(bus_plan)
        if energy_result is not True:
            return st.write(f"The energy result is: {energy_result}")

    if hasattr(w, "warning") and callable(w.warning):
        warning_result = w.warning(bus_plan)
        if warning_result is not False:
            return st.write(f"There were warnings: {warning_result}")

    return True
    if not isinstance(import_result, tuple) or len(import_result) != 2:
        return False
    if import_result[0] is False:
        return import_result[1],

    bus_plan = import_result[1]

    bus_result = verify_bus(bus_plan)
    if bus_result is not True:
        return bus_result,

    critical_result = verify_critical(bus_plan, distance_matrix, merged)
    if critical_result is not True:
        return st.write(f"the critical result is: {critical_result}")

    if hasattr(e, "validate_energy") and callable(e.validate_energy):
        energy_result = e.validate_energy(bus_plan)
        if energy_result is not True:
            return st.write(f"The energy result is: {energy_result}")

    if hasattr(w, "warning") and callable(w.warning):
        warning_result = w.warning(bus_plan)
        if warning_result is not False:
            return st.write(f"There were warnings: {warning_result}")

    return True


print('checker: main OK')