import pandas as pd

from busplanner.calculations.checker.errors import start_garage
from busplanner.calculations.checker.imports import import_bus_plan
from busplanner.calculations.grade.kpi import efficiency
from busplanner.calculations.improver.gantt import plot_gantt
from busplanner.website.check import get_bus_schedule_warnings
from busplanner.website.results import _load_plot_gantt


def test_accepts_excel_style_column_names_and_garage_aliases():
    df = pd.DataFrame(
        {
            "Bus": [1, 1],
            "Start Time": [0, 60],
            "End Time": [30, 90],
            "Start Location": ["Garage", "EHV GARAGE"],
            "End Location": ["EHV GARAGE", "Garage"],
            "Activity": ["idle", "idle"],
            "Service Line": [None, None],
            "Energy Consumption": [1.0, 1.0],
        }
    )

    normalized = import_bus_plan(df)

    assert list(normalized.columns) == [
        "bus",
        "start time",
        "end time",
        "start location",
        "end location",
        "activity",
        "line",
        "energy consumption",
        "duration",
    ]
    assert normalized["start location"].tolist() == ["ehvgar", "ehvgar"]
    assert normalized["end location"].tolist() == ["ehvgar", "ehvgar"]


def test_accepts_common_garage_location_aliases():
    df = pd.DataFrame(
        {
            "bus": [1, 1],
            "start location": ["Garage", "EHVGAR"],
            "end location": ["EHVGAR", "Garage"],
            "start time": [0, 60],
            "end time": [30, 90],
            "activity": ["idle", "idle"],
            "line": [None, None],
            "energy consumption": [1.0, 1.0],
        }
    )

    assert start_garage(df) is True


def test_warns_when_idle_rows_have_missing_energy_values():
    df = pd.DataFrame(
        {
            "start location": ["garage", "stop"],
            "end location": ["garage", "garage"],
            "start time": [0, 30],
            "end time": [20, 50],
            "activity": ["idle", "service trip"],
            "line": [None, 401],
            "bus": [1, 1],
            "energy consumption": [None, 12.0],
        }
    )

    warnings = get_bus_schedule_warnings(df)

    assert "Idle rows in the bus schedule are missing energy consumption values." in warnings


def test_returns_empty_warning_list_for_valid_schedule():
    df = pd.DataFrame(
        {
            "activity": ["idle", "service trip"],
            "energy consumption": [1.5, 12.0],
            "start location": ["garage", "garage"],
            "end location": ["garage", "stop"],
            "start time": [0, 15],
            "end time": [10, 30],
            "line": [None, 401],
            "bus": [1, 1],
        }
    )

    assert get_bus_schedule_warnings(df) == []


def test_efficiency_accepts_legacy_energy_column_names():
    schedule = pd.DataFrame({"energy consumption": [10.0, 10.0]})
    merged = pd.DataFrame({"energy consumption": [20.0, 20.0]})

    assert efficiency(schedule, merged) == 2.0


def test_plot_gantt_accepts_hhmmss_string_times():
    df = pd.DataFrame(
        {
            "bus": [1, 1],
            "start time": ["00:00:00", "01:00:00"],
            "end time": ["00:30:00", "01:45:00"],
            "activity": ["idle", "service trip"],
        }
    )

    fig = plot_gantt(df)

    assert fig is not None
    assert len(fig.axes) == 1


def test_website_loader_exposes_time_converter_for_gantt():
    plot_fn = _load_plot_gantt()

    assert callable(plot_fn)
