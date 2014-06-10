import copy
from datetime import datetime
import re
__author__ = 'sajith'

class AbstractParser:
    def parse(self, location):
        pass


class GoogleCalendarParser(AbstractParser):
    def parse(self, file):
        data = file.readlines()
        taskBaseDate = None
        tasks = []
        for row in data:
            dateMatch = re.search('(Sun|Mon|Tue|Wed|Thu|Fri|Sat) (Jan|Feb|Mar|April|May|Jun|July|Aug|Sept|Oct|Nov|Dec) (\d+)',row)
            if (dateMatch is not None):
                dateStr = dateMatch.group(0)
                row = row[len(dateStr):]
                row = row.lstrip()
                dateStr += " " + str(datetime.today().year)
                taskBaseDate = datetime.strptime(dateStr, "%a %b %d %Y")

            timeMatch = re.search("\d+:\d+(am|pm)",row)
            if (timeMatch is not None):

                timeStr = timeMatch.group(0)
                row = row.lstrip()
                taskStr = row[len(timeStr):]
                taskStr = taskStr.lstrip().rstrip()

                taskDate = datetime.strptime(taskBaseDate.strftime("%Y %b %d")+" " + timeStr, "%Y %b %d %I:%M%p")
                print(taskBaseDate.strftime("%Y %b %d")+" " + timeStr)
                tasks.append([taskStr,taskDate.strftime('%Y-%m-%d %H:%M')])
        return tasks

class ParserFactory:
    def getParser(self, parserType):
        if (parserType == "google"):
            return GoogleCalendarParser()
        else:
            raise Exception