from index import Index
from datetime import datetime
from datetime import timedelta
from time import sleep
from parser import ParserFactory
from print_plugin import TextDecoratorPlugin, PaddedDecoratorPlugin, ConkyColoredDecoratorPlugin, HumanizedDatesPlugin, \
    TrimLongNamesPlugin
import pynotify
import argparse

__author__ = 'sajith'

import sys
from subprocess import call

index = Index("/home/sajith/.task")


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
        name = params[0].replace("\"", "")
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
        index.addTask(name, date, recurrence)


    def parseDate(self, date):
        #see its a tagged date
        dateStrs = date.split(",")
        if (len(dateStrs) > 1):
            #tagged date with time
            datePart = self.__getDate__(dateStrs[0])
            timePart = datetime.strptime(dateStrs[1], '%H:%M').time()
            return datetime.combine(datePart, timePart)
        elif (len(dateStrs) == 1):  #single date, either tag or formatted
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
        print("Entering into notification loop...")
        for overdueTask in tasksTobeNotified[0]:
            pynotify.init("markup")
            n = pynotify.Notification(" ************** TASK NOTIFICATION **************\n",
                                      "<b>Task Name</b> <i>" + overdueTask.taskName + " (" + str(
                                          overdueTask.id) + ")</i> <b>" + self.getDueTime(
                                          overdueTask.dueIn, True) + "</b>",
                                      "/home/sajith/scratch/mytodo/Task-List-icon.png")
            n.show()
            sleep(2)

        for starting in tasksTobeNotified[1]:
            pynotify.init("markup")
            n = pynotify.Notification(" ************** TASK NOTIFICATION **************\n",
                                      "<b>Task Name</b> <i>" + starting.taskName + " (" + str(
                                          starting.id) + ")</i> <b>" + self.getDueTime(
                                          starting.dueIn, False) + "</b>",
                                      "/home/sajith/scratch/mytodo/Task-List-icon.png")
            n.show()
            sleep(2)


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

    def getDueTime(self, time, isOverdue):
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

        today = datetime.today().date()

        todaysTasks = [task for task in taskWithDates if
                       not hasattr(task.date, "time") or task.date.strftime('%H:%M') == "00:00"]

        alltasks = todaysTasks + taskWithoutDates

        if (len(alltasks) > 0):
            # print("${color A8A8A8}")
            for task in alltasks:
                print(str(task.id) + " " + task.taskName)
                # print("(" + textDeco.getTaskId(task.id, task) + ")" + textDeco.getTaskName(task.taskName, task))
        else:
            print("You got nothing todo")
            print("Perhaps you should find some work or a new job ????")

    def agenda(self, pluginType):
        # print(" \n")
        today, upcoming = index.agenda()
        textDeco = self.__getTextDecorator__(pluginType)

        if (len(today) == 0):
            print "${font Inconsolata:italic:size=12}Nothing scheduled for today${font}"
            print("")
        else:
            for task in today:
                print(str(textDeco.getTaskId(task.id, task)) + textDeco.getTaskName(task.taskName, task) + str(textDeco.getDueDate(task.date, task)))
            print "${font}"
        print("")

        if(pluginType == "conky"):
            print "${font Inconsolata:size=12}"
        for task in upcoming:
            print(str(textDeco.getTaskId(task.id, task)) + textDeco.getTaskName(task.taskName, task) + str(textDeco.getDueDate(task.date, task)))

        if(pluginType == "conky"):
            print "${font}"


    def __getTextDecorator__(self, pluginType):
        if (pluginType == "conky"):
            return HumanizedDatesPlugin(TrimLongNamesPlugin(PaddedDecoratorPlugin(5, 10, 40, ConkyColoredDecoratorPlugin(TextDecoratorPlugin()))))
        else:
            return TextDecoratorPlugin()

    def importTasks(self, parserType="google", location="google"):
        parser = ParserFactory().getParser(parserType)
        stringTasks = parser.parse(file(location))
        index.importTask(stringTasks)

    def snooze(self, args):
        snoozeTime = 15
        if (len(args) == 2):
            snoozeTime = int(args[1])

        index.snooze(args[0], snoozeTime)

    def gc(self):
        index.gc()


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("command", choices=["add", "short", "agenda", "todo", "done", "notify", "import", "snooze", "gc"])
    parser.add_argument("command_args", nargs="*")
    parser.add_argument("--type", help="increase output verbosity", default="terminal")
    args = parser.parse_args()

    operation = args.command

    # for arg in sys.argv:
    #     print(arg)

    if (operation == "short"):
        Todo().listShort()
    elif (operation == "long"):
        Todo().listDetails()
    elif (operation == "delete"):
        Todo().delete(int(sys.argv[2]))
    elif (operation == "done"):
        Todo().complete(sys.argv[2])
    elif (operation == "add"):
        Todo().add(sys.argv[2:len(sys.argv)])
    elif (operation == "notify"):
        Todo().notifyAll()
    elif (operation == "todo"):
        Todo().listTodos()
    elif (operation == "agenda"):
        Todo().agenda(args.type)
    elif (operation == "import"):
        Todo().importTasks("google", sys.argv[2])
    elif (operation == "snooze"):
        Todo().snooze(sys.argv[2:])
    elif (operation == "gc"):
        Todo().gc()


if __name__ == "__main__":
    main()