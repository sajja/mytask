import datetime
from dateutil import get_floor_time, get_time_as_str

__author__ = 'sajith'


class PrintPlugin:
    def printTaskName(self, task):
        print(task.taskName)

    def printDueDate(self, task):
        print(task.date)

    def printTaskId(self, task):
        print(task.id)


class TextDecoratorPlugin:
    def getTaskName(self, task):
        return task

    def getDueDate(self, task):
        return task

    def getTaskId(self, task):
        return task


class PaddedDecoratorPlugin(TextDecoratorPlugin):
    def __init__(self, taskIdWidth, dateWidth, taskWidth, decorator):
        self.decorator = decorator
        self.taskIdWidth = taskIdWidth
        self.dateWidth = dateWidth
        self.taskWidth = taskWidth

    def getTaskName(self, task):
        return self.decorator.getTaskName(self.__getText__(str(task), self.taskWidth))

    def getDueDate(self, task):
        return self.decorator.getTaskName(self.__getText__(str(task), self.dateWidth))

    def getTaskId(self, task):
        return self.decorator.getTaskId(self.__getText__(str(task), self.taskIdWidth))

    def __getText__(self, text, padding):
        return self.__pad__(text, padding)

    def __pad__(self, string, size):
        appendLen = size - string.__len__()
        if appendLen > 0:
            for i in range(appendLen):
                string += " "
        return string


class ConkyColoredDecoratorPlugin(TextDecoratorPlugin):
    def __init__(self, decorator):
        self.decorator = decorator

    def getTaskName(self, task):
        # task = "${color 9999FF}" + task + "${color}"
        return self.decorator.getTaskName(task)

    def getDueDate(self, task):
        # task.taskName = "${color 9999FF}" + task.date + "${color}"
        return self.decorator.getTaskName(task)

    def getTaskId(self, task):
        # task = "${color 9999FF}" + task + "${color}"
        return self.decorator.getTaskId(task)


class HumanizedDatesPlugin(TextDecoratorPlugin):
    def __init__(self, decorator):
        self.decorator = decorator

    def getDueDate(self, task):
        return self.decorator.getDueDate(self.__get_humanized_date__(task))

    def getTaskName(self, task):
        return self.decorator.getTaskName(task)

    def getTaskId(self, task):
        return self.decorator.getTaskId(task)

    def __get_humanized_date__(self, date):
        now = datetime.datetime.now()
        if (get_floor_time(date) == get_floor_time(now)):
            return "Today" + get_time_as_str(date)
        elif (get_floor_time(date) == get_floor_time((now + datetime.timedelta(days=1)))):
            return "Tomorrow" + get_time_as_str(date)
        elif (get_floor_time(date) == get_floor_time(now + datetime.timedelta(days=2))):
            return "Day after tomorrow"
        elif (get_floor_time(date) < get_floor_time(now)):
            return "Ovedue by " + str((now - get_floor_time(date)).days) + " Days"
        else:
            return "Later (" + str(date.day) + "/" + str(date.month) + ")"

            # def get_floor_time(self, date):
            #     if (hasattr(date,"time")):
            #         return date.replace(hour=0,minute=0,second=0,microsecond=0)
            #     else:
            #         return datetime.datetime.combine(date,datetime.time(0,0,0,0))
            #
            # def get_time_as_str(self,date):
            #     if (hasattr(date,"time")):
            #         return " - " +str(date.time().hour) + ":" + str(date.time().minute)
            #     else:
            #         return ""


def main():
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    future = today + datetime.timedelta(days=2)
    future2 = today + datetime.timedelta(days=6)
    overdue = today + datetime.timedelta(days=-6)

    print(future2 - today).days
    HumanizedDatesPlugin(None).get_floor_time(today.date())
    HumanizedDatesPlugin(None).get_floor_time(today)

    print(HumanizedDatesPlugin(TextDecoratorPlugin()).getDueDate(today.date()))
    print(HumanizedDatesPlugin(TextDecoratorPlugin()).getDueDate(today))
    print(HumanizedDatesPlugin(TextDecoratorPlugin()).getDueDate(tomorrow))
    print(HumanizedDatesPlugin(TextDecoratorPlugin()).getDueDate(tomorrow.date()))
    print(HumanizedDatesPlugin(TextDecoratorPlugin()).getDueDate(future))
    print(HumanizedDatesPlugin(TextDecoratorPlugin()).getDueDate(future.date()))
    print(HumanizedDatesPlugin(TextDecoratorPlugin()).getDueDate(future2))
    print(HumanizedDatesPlugin(TextDecoratorPlugin()).getDueDate(future2.date()))

    print(HumanizedDatesPlugin(TextDecoratorPlugin()).getDueDate(overdue))
    print(HumanizedDatesPlugin(TextDecoratorPlugin()).getDueDate(overdue.date()))


if __name__ == "__main__":
    main()