from index import Index
from datetime import datetime
from datetime import timedelta
from time import sleep
from print_plugin import TextDecoratorPlugin, PaddedDecoratorPlugin, ConkyColoredDecoratorPlugin, HumanizedDatesPlugin

__author__ = 'sajith'

import sys
from subprocess import call

index = Index()


class Todo:
    def __init__(self):
        pass

    def printTodoList(self):
        pass

    def listShort(self, status="PENDING", date=None):
        taskWithDates, taskWithoutDates = index.listAll()
        print("Id  Due date              Task")
        print("--  --------              ----")
        allTasks = taskWithDates + taskWithoutDates
        for task in allTasks:
            print(self.pad(str(task.id), 4) + self.pad(str(task.date), 22) + str(task.taskName))

    def listDetails(self):
        allTasks = index.listAll()
        print("Id  Due date             Status   Reccrance  Task")
        print("--  --------             -------  ---------  ----")

        for task in allTasks:
            print(self.pad(str(task.id), 4) + self.pad(str(task.date), 21) + self.pad(str(task.status), 9) + self.pad(
                str(task.reccrance), 11) + task.taskName)

    def viewTask(self, taskId):
        pass

    def add(self, params):
        recurrence = None
        date = None
        notify = None
        if (len(params) > 4):
            raise Exception("Too many params")

        #todo do this better
        name = params[0]
        params = params[1:]
        if (len(params) > 0 ):
            date = self.parseDate(params[0])
            recurrence = "NONE"
            notify = "NO"
            params = params[1:]
            if (len(params) > 0):
                recurrence = params[0]
                params = params[1:]
                if (len(params) > 0):
                    notify = params[0]

        print("Task name: " + name)
        print("Dud daet: " + str(date))
        print("Reccurance: " + str(recurrence))
        print("Notify: " + str(notify))
        index.addTask(name, date, recurrence, notify)


    def parseDate(self, date):
        #see its a tagged date
        dateStrs = date.split(",")
        if (len(dateStrs) > 1):
            #tagged date with time
            datePart = self.__getDate__(dateStrs[0])
            timePart = datetime.strptime(dateStrs[1], '%H:%M').time()
            return datetime.combine(datePart, timePart)
        elif (len(dateStrs) == 1):  #single date, either tag or formated
            if (len(date.split(" ")) > 1):
                #formated date with time
                parsedDate = datetime.strptime(date, '%Y-%m-%d %H:%M')
                return parsedDate
            elif len(date.split(" ")) == 1:
                return self.__getDate__(date)
            else:
                raise Exception("Unparsable date " + date)
        else:
            raise Exception("unparsable date " + date)


    def __getDate__(self, date):
        if (date.lower() == "today"):
            return datetime.today().date()
        if (date.lower() == "tomorrow"):
            return datetime.today().date() + timedelta(days=1)
        else:
            parsedDate = datetime.strptime(date, '%Y-%m-%d').date()
            return parsedDate

    def pad(self, string, size):
        appendLen = size - string.__len__()
        if appendLen > 0:
            for i in range(appendLen):
                string += " "
        return string


    def delete(self, id):
        task = index.findTaskById(id)
        if (task != None):
            index.deleteTask(task)
            print("Task delted")
        else:
            print("No task found")


    def complete(self, id):
        index.markTaskComplete(id)


    def searchTask(self, name):
        print("not implemented")


    def notifyAll(self):
        tasksTobeNotified = index.listNotificationsPendingTasks(15)

        for overdueTask in tasksTobeNotified[0]:
            text = "Task: " + overdueTask.taskName + " " + self.getOverdueTime(overdueTask.dueIn, True)
            call("/usr/bin/notify-send \"" + text + "\"", shell=True)
            sleep(2)
            # call("notify-send", overdueTask.taskName + "is overdue")

        for starting in tasksTobeNotified[1]:
            text = "Task: " + starting.taskName + " " + self.getOverdueTime(starting.dueIn, False)
            call("/usr/bin/notify-send \"" + text + "\"", shell=True)
            # sleep(2)


    def listAll(self):
        entries = index.listAll()
        count = 0
        for entry in entries:
            print("Task name: " + entry.taskName)
            print("Task due date: " + str(entry.dateTime))
            print("Recuurance: " + str(entry.reccrance))
            print("Notifications: " + str(entry.notify))
            print("------------------------------------")
            count += 1
        print("Total number of entries " + str(count))

    def getOverdueTime(self, time, isOverdue):
        if (time == 0 and isOverdue):
            return "just passed the scheduled time"
        elif (time == 0 and not isOverdue):
            return "is just strating"
        elif (isOverdue):
            return "is overdue by " + str(time) + " min"
        elif (not isOverdue):
            return "will start in " + str(time) + " min"

    def listTodos(self):
        taskWithDates, taskWithoutDates = index.listAll()
        textDeco = self.__getTextDecorator__("conky")
        print("${color 00FF00}")
        print("Task Id       Task Name")
        print("-------       --------- ${color}")
        for task in taskWithoutDates:
            print(textDeco.getTaskId(task.id) + textDeco.getTaskName(task.taskName))

    def agenda(self):
        taskWithDates, taskWithoutDates = index.listAll()
        textDeco = self.__getTextDecorator__("conky")
        print("${color 00FF00}")
        print("Task Id       Task Name                               Due on")
        print("-------       ---------                               --------------- ${color}")
        for task in taskWithDates:
            print(textDeco.getTaskId(task.id) + textDeco.getTaskName(task.taskName) + textDeco.getDueDate(task.date))

    def __getTextDecorator__(self, pluginType):
        if (pluginType == None):
            return TextDecoratorPlugin()
        elif (pluginType == "conky"):
            return HumanizedDatesPlugin(
                PaddedDecoratorPlugin(14, 10, 40, ConkyColoredDecoratorPlugin(TextDecoratorPlugin())))


def main():
    if len(sys.argv) <= 1:
        print("Usage: todo <listall>")
        exit()
    if (sys.argv[1] == "short"):
        Todo().listShort()
    elif (sys.argv[1] == "long"):
        Todo().listDetails()
    elif (sys.argv[1] == "delete"):
        Todo().delete(int(sys.argv[2]))
    elif (sys.argv[1] == "complete"):
        Todo().complete(sys.argv[2])
    elif (sys.argv[1] == "add"):
        Todo().add(sys.argv[2:len(sys.argv)])
    elif (sys.argv[1] == "notify"):
        Todo().notifyAll()
    elif (sys.argv[1] == "todo"):
        Todo().listTodos()
    elif (sys.argv[1] == "agenda"):
        Todo().agenda()
    else:
        print("Unknown command")


if __name__ == "__main__":
    main()