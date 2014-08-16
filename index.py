import copy
from dateutil import get_floor_time, dateDiff

__author__ = 'sajith'

import datetime
from os import listdir
from os.path import isfile, join
import hashlib
import os


class Index:
    entries = []
    lastIndex = 0

    def listAll(self, status="PENDING"):
        tasksWithSetDate = sorted(
            [entry for entry in self.entries if ((entry.status == status or status == None)) and entry.date != None],
            key=lambda task: task.date)
        taskWithoutDate = sorted(
            [entry for entry in self.entries if ((entry.status == status or status == None)) and entry.date == None],
            key=lambda task: task.id)
        return (tasksWithSetDate, taskWithoutDate)

    def listTodayTasks(self):
        today = datetime.datetime.today().date()

        todayTasks = [task for task in self.entries if (task.date != None and task.date.date() == today)]
        return todayTasks

    def listNotificationsPendingTasks(self, future=10):
        # we go back "future" number of min
        move_N_number_of_min_into_past = datetime.datetime.now() + datetime.timedelta(minutes=-future)
        # unitl this its overdue tasks
        overdueTime = move_N_number_of_min_into_past + datetime.timedelta(minutes=future)
        #tasks to be soon started.
        soonStartTime = overdueTime + datetime.timedelta(minutes=future)

        taskWithDate, taskWithoutDate = self.listAll()
        allPendingTasks = taskWithDate + taskWithoutDate

        overdueTasks = []
        startingSoonTasks = []

        for entry in allPendingTasks:
            #If this is a past recrrence task, we nee to check if the time criteria meets. So bring the date to today for easier comparison.
            normalizedEntryDate = self.normalizeIfReccrentTask(entry, move_N_number_of_min_into_past)

            if normalizedEntryDate != None:
                if normalizedEntryDate >= move_N_number_of_min_into_past and normalizedEntryDate <= overdueTime and self.__should_notify__(
                        entry):
                    entry.dueIn = (overdueTime - normalizedEntryDate).seconds / 60
                    overdueTasks.append(entry)
                elif normalizedEntryDate > overdueTime and normalizedEntryDate <= soonStartTime and self.__should_notify__(
                        entry):
                    entry.dueIn = (normalizedEntryDate - overdueTime).seconds / 60
                    startingSoonTasks.append(entry)
                    # AbstractParser.parse(self, location)
        return (overdueTasks, startingSoonTasks)

    def importTask(self, taskList):
        for task in taskList:
            taskStr = "|".join([part for part in task])
            taskStr += "|NONE|PENDING"
            taskId = hashlib.sha1()
            taskId.update(taskStr)
            id = taskId.hexdigest()
            if (not self.hasTask(id)):
                self.addTask(task[0], datetime.datetime.strptime(task[1], "%Y-%m-%d %H:%M"), "NONE")

    def hasTask(self, hash):
        for task in self.entries:
            if task.internalId == hash:
                return True
        return False

    def normalizeIfReccrentTask(self, task, now):
        if task.reccrance != None and task.date < now and self.isItToday(task.date, now, task.reccrance) == True:
            taskTime = task.date.time()
            return datetime.datetime.combine(now, taskTime)
        else:
            return task.date

    def isItToday(self, taskDate, today, rec):
        if rec == "DAILY":
            return True
        elif rec == "WEEKLY":
            if taskDate.weekday() == today.weekday():
                return True
            else:
                return False
        elif rec == "NONE":
            return False
        else:
            raise Exception("Unsupported reccurence" + rec)

    def snooze(self, taskId, time=5):
        task = self.findTaskById(taskId)
        task.set_property("SNOOZE", time)
        task.set_property("LAST_SNOOZED", datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        self.__update_task__(task)

    def addTask(self, name, taskDate=None, rec=None):
        now = datetime.datetime.now()
        taskStr = name
        if (taskDate != None):
            taskStr += "|"
            taskStr += taskDate.strftime('%Y-%m-%d %H:%M')
        if (rec != None):
            taskStr += "|"
            taskStr += rec
        taskStr += "|PENDING"

        task = Task(str(self.__getNewTaskId__()) + "|" + taskStr)
        task.set_property("CREATED", now.strftime('%Y-%m-%d %H:%M'))
        self.entries.append(task)
        self.__write_to_fs__(task, self.getTaskHash(task))
        return task

    def deleteTask(self, task):
        taskFile = self.indexDir + "/" + self.getTaskHash(task)
        if os.path.isfile(taskFile):
            os.unlink(taskFile)
        self.__init__()


    def markTaskComplete(self, taskId):
        task = self.findTaskById(taskId)
        task.status = "DONE"
        self.__update_task__(task)
        return task

    def findTaskById(self, taskId, status="PENDING"):
        for task in self.entries:
            if str(task.id) == str(taskId) and task.status == status:
                return task
        return None

    def gc(self):
        self.lastIndex = 0
        self.__sync_last_task_id__()
        more_than_one_month_ago = datetime.datetime.today() + datetime.timedelta(days=-31)

        for task in self.entries:
            created = task.get_property("CREATED")
            createdDate = None
            if (created != None):
                createdDate = datetime.datetime.strptime(created, "%Y-%m-%d %H:%M")

            if (task.status == "DONE"):
                self.deleteTask(task)
            elif createdDate != None and createdDate < more_than_one_month_ago:
                self.deleteTask(task)
            elif task.date != None and task.date < more_than_one_month_ago:
                self.deleteTask(task)

        for task in self.entries:
            task.id = self.__getNewTaskId__()
            self.__write_to_fs__(task, task.internalId)

    def __sync_last_task_id__(self):
        keyFile = file(self.indexDir + "/key", "w")
        keyFile.write(str(self.lastIndex))
        keyFile.flush()
        # AbstractParser.parse(self, location)
        keyFile.close()

    def __getNewTaskId__(self):
        self.lastIndex += 1
        self.__sync_last_task_id__()
        return self.lastIndex

    def __write_to_fs__(self, task, fileName):
        todofile = file(self.indexDir + "/" + fileName, "w")
        todofile.write(task.toString())
        todofile.flush()
        todofile.close()
        self.__init__()

    def getTaskHash(self, task):
        taskId = hashlib.sha1()
        taskWithoutId = "|".join([part for part in task.toString().split("|")[1:]])

        taskId.update(taskWithoutId)
        return taskId.hexdigest()

    def updateTask(self, id, newData):
        pass

    def agenda(self):
        now = datetime.datetime.now()
        taskWithDate, taskWithoutDate = self.listAll()
        todaysAgenda = []
        upcoming = []
        for task in taskWithDate:
            dd, weekDayDiff = dateDiff(now, task.date)

            if (task.reccrance == "DAILY" and task.date <= now):
                copyOfTheTask = self.shallowCopyATask(task, now)
                tomorrowsTask = self.shallowCopyATask(task, now + datetime.timedelta(days=1))
                todaysAgenda.append(copyOfTheTask)
                upcoming.append(tomorrowsTask)
            elif (get_floor_time(task.date) == get_floor_time(now)):
                todaysAgenda.append(task)
            elif (task.reccrance == "WEEKLY" and task.date <= now and weekDayDiff == 0):
                copyOfTheTask = self.shallowCopyATask(task, now)
                todaysAgenda.append(copyOfTheTask)
            elif (weekDayDiff <= 3 and ( (task.reccrance != None and task.reccrance != "NONE") or task.date > now)):
                # shallowCopyiedTask = self.shallowCopyATask(task, now + datetime.timedelta(days=daysBetweenTasks))
                upcoming.append(task)
        return todaysAgenda, upcoming

    def shallowCopyATask(self, task, dateToBeUpdated):
        shallowCopiedTask = copy.copy(task)
        if (hasattr(task.date, "time")):
            dateToBeUpdated = datetime.datetime.combine(dateToBeUpdated, task.date.time())
        else:
            dateToBeUpdated = dateToBeUpdated.date()
        shallowCopiedTask.date = dateToBeUpdated

        return shallowCopiedTask

    def __init__(self, indexDir=None):
        self.entries = []
        if indexDir == None:
            indexDir = "./.task"

        self.indexDir = indexDir

        taskFiles = [taskFile for taskFile in listdir(indexDir) if
                     isfile(join(indexDir, taskFile)) and taskFile != "key"]

        self.__createEntries__(indexDir, taskFiles)
        self.__readLastIndex__()


    def __readLastIndex__(self):
        keyFile = file(self.indexDir + "/key", "a+")
        data = keyFile.readline()
        if (data != ""):
            self.lastIndex = int(data)
        keyFile.close()

    def __createEntries__(self, baseDir, taskFiles):
        for filename in taskFiles:
            taskFile = file(baseDir + "/" + filename)
            lines = taskFile.readlines()
            rowData = lines[0]
            if (len(lines) > 1):
                rowData += lines[1]
            self.entries.append(Task(rowData, filename))
            taskFile.close()

    def __update_task__(self, task):
        self.__write_to_fs__(task, task.internalId)

    def __should_notify__(self, task):
        snoozed = task.get_property("SNOOZE")
        lastSnoozed = task.get_property("LAST_SNOOZED")
        if (snoozed is not None and lastSnoozed is not None):
            lastSnoozedDate = datetime.datetime.strptime(lastSnoozed, "%Y-%m-%d %H:%M")
            if (lastSnoozedDate + datetime.timedelta(minutes=int(snoozed)) < datetime.datetime.now()):
                return True
            else:
                return False
        return True


class Task:
    taskName = ""
    date = None
    reccrance = None
    # notify = None
    status = None
    id = 0
    snoozed = 0
    dueIn = 0
    internalId = None
    props = {}

    def get_property(self, property):
        return self.props.get(property)

    def set_property(self, property, value):
        self.props[property] = value

    def __init__(self, rowData, fileName=None):
        self.props = {}
        self.__internal_init__(rowData)
        self.internalId = fileName


    def __internal_init__(self, rowData):
        if rowData == None:
            raise Exception("row data cannot be null")
        taskRows = rowData.split("\n")
        mainRow = taskRows[0]
        if (len(taskRows) > 1):
            subRow = taskRows[1]
            props = subRow.split("|")
            for prop in props:
                keyValue = prop.split("=")
                if (len(keyValue) > 1):
                    self.props[keyValue[0]] = keyValue[1]

        parts = mainRow.split("|", 6)
        self.id = int(parts[0])
        self.taskName = parts[1]
        partSize = len(parts)
        if (partSize > 3):
            dateTime = datetime.datetime.strptime(parts[2], '%Y-%m-%d %H:%M')
            self.date = dateTime
            self.hour = dateTime.time().hour
            self.min = dateTime.time().minute
            self.reccrance = parts[3]
            self.status = parts[4]
        else:
            self.status = parts[2]

    def isOverdue(self):
        return self.date >= datetime.datetime.today() + datetime.timedelta(minutes=30)

    def get_main_part_as_string(self):
        taskStr = str(self.id) + "|" + self.taskName
        if (self.date != None):
            taskStr += "|"
            taskStr += self.date.strftime('%Y-%m-%d %H:%M')
        if (self.reccrance != None):
            taskStr += "|"
            taskStr += self.reccrance
        # if (self.notify != None):
        # taskStr += "|"
        # taskStr += self.notify
        taskStr += "|"
        taskStr += self.status
        return taskStr

    def toString(self):
        mainPart = self.get_main_part_as_string()

        if (len(self.props) > 0):
            mainPart += "\n"
            for prop in self.props:
                mainPart += prop + "=" + str(self.props[prop])
                mainPart += "|"

        return mainPart
