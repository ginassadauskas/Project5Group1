"""Default and configurable values.
"""

"""Power variables
"""
# SOH is the estimated state of health of the buses deployed. 
#   If the SOH is None, there is no estimation, every bus has a predetermined/precalculated SOH 
SOH: tuple[float, float] | None = (0.85, 0.95)

# Safety Margin is the minimum SOC that a bus must keep before charging.
SAFETY_MARGIN: float = 0.1 #10%

# Maximum battery capacity of a bus, ignoring the buses' State of Healths.
# SOC is the current energy level, or State of Charge, in kWh.
MAX_SOC: int = 300 #kWh
# The % of starting State of Charge, taken from the max soc or equal to the SOH, if MAX_SOC * SOC > SOH. 
SOC: float = 0.9
# If False (default), the starting SOC is calculated using the SOH instead of MAX_SOC.
ABSOLUTE_SOC: bool = False 

# Idle consumption is the amount of kWh per minute a bus consumes while it is idling.
IDLE: float = 1/12 #kW

# How fast do chargers charge?
# A bus charges at the fast charge rate while its SOC is lower than the threshold.
FAST_CHARGE: int = 450 #kW
SLOW_THRESHOLD: float = 0.9 #90% of the bus's SOH
# ABSOLUTE_THRESHOLD = SOH * SLOW_THRESHOLD
SLOW_CHARGE: int = 60 #kW

#The estimated average consumption for a bus to move 1m.
#   Default is calculated as the average of the given range (0.7, 2.5)kWh/km
CON_PER_M: int = 0.0016 #kW

"""Import variables
"""
#At what time (in minutes) does the schedule consider it a new day.
MIDNIGHT: int = 180

"""Checker variables
"""
#A list with each charging spot
CHARGER: list[str] = ['ehvgar']


print('calculations: defaults.py OK')