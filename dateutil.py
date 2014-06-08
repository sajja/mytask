__author__ = 'sajith'

from datetime import datetime
from datetime import timedelta

def get_floor_time(date):
    if (hasattr(date, "time")):
        return date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        return datetime.combine(date, datetime.time(0, 0, 0, 0))


def get_time_as_str( date):
    if (hasattr(date, "time")):
        timeStr = date.strftime("%H:%M")
        if timeStr == "00:00":
            timeStr=""
        return timeStr
    else:
        return ""

def weekDayDiff(start, end):
    days = 0
    while (start != end):
        start +=1
        days +=1
        if(start >= 7):
            start=0
    return days


def dateDiff(date1, date2):
    dd = abs((date1 - date2).days)

    return dd,weekDayDiff(date1.weekday(), date2.weekday())


def count(date1, date2):
    days = 0
    while (date1 < date2):
        days +=1
        date1 = date1 + timedelta(days=1)

    return days

def main():
    today = datetime.today()
    yesterday = today + timedelta(days=-1)
    tomorrow = today + timedelta(days=1)
    dayAfterTomorrow = today + timedelta(days=2)
    nextweekSameday = today + timedelta(days=7)
    nextweekTomorrow = today + timedelta(days=-5)

    x = dateDiff(nextweekTomorrow,today )
    y = dateDiff(today, yesterday)
    print("Count days " + str(x))
    print("Weekday diff " + str(x%7))
if __name__ == "__main__":
    main()

    # 2014-06-03 17:16:00