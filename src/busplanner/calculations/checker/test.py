from pathlib import Path

import pandas as pd
from busplanner.calculations.checker.errors import overlaps
from busplanner.calculations.checker.imports import import_bus_plan


bus_plan = import_bus_plan(pd.read_excel("Bus Planning.xlsx"))
print(overlaps(import_bus_plan(bus_plan)))

