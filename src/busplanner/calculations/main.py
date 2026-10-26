"""Functions necessary to run the website.
"""
import pandas as pd
from .checker.main import verify_schedule
from .imports import merge_route_plan

def merged(timetable, distancematrix):
    """Merges and prepares the timetable and distancematrix for further use.
    
    See calculations/imports.py line 49-72
    """
    return merge_route_plan(timetable, distancematrix)
