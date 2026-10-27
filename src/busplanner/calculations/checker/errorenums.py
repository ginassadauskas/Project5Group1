
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

print('checker: errorenums.py OK')