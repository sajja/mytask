__author__ = 'sajith'

from datetime import datetime

def get_floor_time(date):
    if (hasattr(date, "time")):
        return date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        return datetime.combine(date, datetime.time(0, 0, 0, 0))


def get_time_as_str( date):
    if (hasattr(date, "time")):
        return " - " + str(date.time().hour) + ":" + str(date.time().minute)
    else:
        return ""

def countDays(start, end):
    days = 0
    while (start != end):
        start +=1
        days +=1
        if(start >= 7):
            start=0
    return days