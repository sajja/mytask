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
    def getTaskName(self, taskName, task):
        return taskName

    def getDueDate(self, taskName, task):
        return taskName

    def getTaskId(self, taskName, task):
        return taskName


class PaddedDecoratorPlugin(TextDecoratorPlugin):
    def __init__(self, taskIdWidth, dateWidth, taskWidth, decorator):
        self.decorator = decorator
        self.taskIdWidth = taskIdWidth
        self.dateWidth = dateWidth
        self.taskWidth = taskWidth

    def getTaskName(self, taskName, task):
        return self.decorator.getTaskName(self.__getText__(str(taskName), self.taskWidth), task)

    def getDueDate(self, taskName, task):
        return self.decorator.getDueDate(self.__getText__(str(taskName), self.dateWidth), task)

    def getTaskId(self, taskName, task):
        return self.decorator.getTaskId(self.__getText__(str(taskName), self.taskIdWidth), task)

    def __getText__(self, text, padding):
        return self.__pad__(text, padding)

    def __pad__(self, string, size):
        appendLen = size - string.__len__()
        if appendLen > 0:
            for i in range(appendLen):
                string += " "
        return string


class ConkyColoredDecoratorPlugin(TextDecoratorPlugin):
    todayTasks = "${color FFFFFF}${task}${color}"
    tomorrowTasks = "${color 999999}${task}${color}"
    laterTasks = "${color 999999}${task}${color}"

    def __init__(self, decorator):
        self.decorator = decorator

    def getTaskName(self, taskName, task):
        taskDate = task.date
        today = datetime.datetime.now()
        if (hasattr(taskDate, "time")):
            taskDate = taskDate.date()
        coloredTask = self.__get_colored_output__(taskName, taskDate, today)

        return self.decorator.getTaskName(coloredTask, task)

    def getDueDate(self, taskName, task):
        coloredText = self.decorator.getDueDate(taskName, task)
        taskDate = task.date
        today = datetime.datetime.now()
        if (hasattr(taskDate, "time")):
            taskDate = taskDate.date()

        coloredText = self.__get_colored_output__(coloredText, taskDate, today)

        return coloredText

    def getTaskId(self, taskName, task):
        # coloredText = ""
        today = datetime.datetime.now()
        taskDate = task.date
        if (hasattr(taskDate, "time")):
            taskDate = taskDate.date()
        coloredText = self.__get_colored_output__(taskName, taskDate, today)
        return self.decorator.getTaskId(coloredText, task)

    def __get_colored_output__(self, text, taskDate, today):
        todayDate = today.date()
        if (taskDate == todayDate):
            return self.todayTasks.replace("${task}", text)
        elif (taskDate > todayDate and taskDate < (todayDate + datetime.timedelta(days=2))):
            return self.tomorrowTasks.replace("${task}", text)
        elif (taskDate >= (todayDate + datetime.timedelta(days=2))):
            return self.laterTasks.replace("${task}", text)


class HumanizedDatesPlugin(TextDecoratorPlugin):
    def __init__(self, decorator):
        self.decorator = decorator

    def getDueDate(self, taskName, task):
        return self.decorator.getDueDate(self.__get_humanized_date__(taskName), task)

    def getTaskName(self, taskName, task):
        return self.decorator.getTaskName(taskName, task)

    def getTaskId(self, taskName, task):
        return self.decorator.getTaskId(taskName, task)

    def __get_humanized_date__(self, date):
        now = datetime.datetime.now()
        if (get_floor_time(date) == get_floor_time(now)):
            return "Today " + get_time_as_str(date)
        elif (get_floor_time(date) == get_floor_time((now + datetime.timedelta(days=1)))):
            return "Tomorrow " + get_time_as_str(date)
        # elif (get_floor_time(date) == get_floor_time(now + datetime.timedelta(days=2))):
        #     return "Day after tomorrow "
        # elif (get_floor_time(date) < get_floor_time(now)):
        #     return "Overdue by " + str((now - get_floor_time(date)).days) + " Days"
        else:
            return "Later (" + str(date.day) + "/" + str(date.month) + ")"


class TrimLongNamesPlugin(TextDecoratorPlugin):
    def __init__(self, decorator):
        self.decorator = decorator

    def getDueDate(self, taskName, task):
        return self.decorator.getDueDate(taskName, task)

    def getTaskName(self, taskName, task):
        if (len(taskName) > 35):
            taskName = taskName[0:33]
            taskName += ".."
        return self.decorator.getTaskName(taskName, task)

    def getTaskId(self, taskName, task):
        return self.decorator.getTaskId(taskName, task)


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