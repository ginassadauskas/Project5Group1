~~time values stored in minutes~~

CHECKS:

~~if 2 buses on the same line idle at the same location at the same time (if time overlaps) - raise error~~

~~In a chronological order sort trip rows by start time ascending and check if the trip start\_min is equal previous rows end\_min, return true if fine, otherwise mention time frame of gap (warning)~~

~~the bus's start location on the next trip should match the location at the end of the previous trip - raise error~~

~~&#x20;the first AND last trip of the day of each bus must be the garage (start location for first trip, end location for last trip) - verify first~~

~~&#x20;~~

~~values in the line section for service trips MUST have a value -raise error~~

~~for each row end\_time must be higher than start\_time, or must be considered midnight so say if it goes from 23:50 00:10, 00:10 must be consideed higher minutes  technically~~ solved

~~charging activity must give negative energy consumption, non chargin activities must give positive energy consuption, otherwise return time,activity and energy consumption - raise something~~

*~~if at the END of the trip, a bus has less than capacity(300)\*state\_of\_health(0.95)\*min\_SOH(0.1), it is invalid, return end\_location and end\_time as well (wait on Ivan's data)~~*

AI usage:

in line suggestions were used to formulate doc string text to write it faster

AI was used for debugging and giving examples of some code
