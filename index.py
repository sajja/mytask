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

    def readLastIndex(self):
        keyFile = file(self.indexDir + "/key", "a+")
        data = keyFile.readline()
        if (data != ""):
            self.lastIndex = int(data)
        keyFile.close()

    def __init__(self, indexDir=None):
        self.entries = []
        if indexDir == None:
            indexDir = "./.task"

        self.indexDir = indexDir

        taskFiles = [taskFile for taskFile in listdir(indexDir) if
                     isfile(join(indexDir, taskFile)) and taskFile != "key"]

        self.__createEntries__(indexDir, taskFiles)
        self.readLastIndex()

    def __createEntries__(self, baseDir, taskFiles):
        for filename in taskFiles:
            taskFile = file(baseDir + "/" + filename)
            lines = taskFile.readlines()
            rowData=lines[0]
            if (len(lines) > 1):
                rowData +=lines[1]
            self.entries.append(Task(rowData, filename))
            taskFile.close()

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
        #we go back "future" number of min
        move_N_number_of_min_into_past = datetime.datetime.now() + datetime.timedelta(minutes=-future)
        #unitl this its overdue tasks
        overdueTime = move_N_number_of_min_into_past + datetime.timedelta(minutes=future)
        #tasks to be soon started.
        soonStartTime = overdueTime + datetime.timedelta(minutes=future)

        taskWithDate, taskWithoutDate = self.listAll(status=None)
        allPendingTasks = taskWithDate + taskWithoutDate

        overdueTasks = []
        startingSoonTasks = []

        for entry in allPendingTasks:
            #If this is a past recrrence task, we nee to check if the time criteria meets. So bring the date to today for easier comparison.
            normalizedEntryDate = self.normalizeIfReccrentTask(entry, move_N_number_of_min_into_past)

            if normalizedEntryDate != None:
                if normalizedEntryDate >= move_N_number_of_min_into_past and normalizedEntryDate <= overdueTime and self.__shoudl_notify__(entry):
                    entry.dueIn = (overdueTime - normalizedEntryDate).seconds / 60
                    overdueTasks.append(entry)
                elif normalizedEntryDate > overdueTime and normalizedEntryDate <= soonStartTime and self.__shoudl_notify__(entry):
                    entry.dueIn = (normalizedEntryDate - overdueTime).seconds / 60
                    startingSoonTasks.append(entry)
                    # AbstractParser.parse(self, location)
        return (overdueTasks, startingSoonTasks)

    def importTask(self, taskList):
        for task in taskList:
            taskStr = "|".join([part for part in task])
            taskId = hashlib.sha1()
            taskId.update(taskStr)
            taskId.hexdigest()
            if (not self.hasTask(taskId)):
                self.addTask(task[0],datetime.datetime.strptime(task[1],"%Y-%m-%d %H:%M"),"NONE")


    def hasTask(self, hash):
        for task in self.entries:
            if task.internalId == hash:
                return True
        return False

    def normalizedWeeklyTaskStartingInPast(self, task):
        if (task.reccrance == "WEEKLY" and task.date<datetime.datetime.today()):
            return datetime.datetime.combine(datetime.datetime.today().date(), task.date.time())
        else:
            return task.date

    def normalizeIfReccrentTask(self, task, now):
        # if task.reccrance != None and task.date < now and self.isItToday(task.date, now, task.reccrance) == True:
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


    def __shoudl_notify__(self, task):
        snoozed = task.get_property("SNOOZE")
        lastSnoozed = task.get_property("LAST_SNOOZED")
        if (snoozed is not None and lastSnoozed is not None):
            lastSnoozedDate = datetime.datetime.strptime(lastSnoozed,"%Y-%m-%d %H:%M")
            if (lastSnoozedDate + datetime.timedelta(minutes=int(snoozed)) < datetime.datetime.now()):
                return True
            else:
                return False
        return True

    def snooze(self, taskId, time = 5):
        task = self.findTaskById(taskId)
        task.set_property("SNOOZE",time)
        task.set_property("LAST_SNOOZED",datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        self.__update_task__(task)


    def addTask(self, name, datetime=None, rec=None):
        taskStr = name
        if (datetime != None):
            taskStr += "|"
            taskStr += datetime.strftime('%Y-%m-%d %H:%M')
        if (rec != None):
            taskStr += "|"
            taskStr += rec
        taskStr += "|PENDING"

        task = Task(str(self.getNewTaskId()) + "|" + taskStr)
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

    def __sync_last_task_id__(self):
        keyFile = file(self.indexDir + "/key", "w")
        keyFile.write(str(self.lastIndex))
        keyFile.flush()
        # AbstractParser.parse(self, location)
        keyFile.close()

    def getNewTaskId(self):
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

    def __update_task__(self, task):
        self.__write_to_fs__(task, task.internalId)

    def agenda(self):
        now = datetime.datetime.now()
        taskWithDate, taskWithoutDate = self.listAll()
        todaysAgenda = []
        upcoming = []
        for task in taskWithDate:
            # task.date = self.normalizedWeeklyTaskStartingInPast(task)
            dd,weekDayDiff = dateDiff(now, task.date)
            # daysBetweenTasks = countDays(now.weekday(), task.date.weekday())

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
            elif (weekDayDiff <=3 and ( (task.reccrance != None and task.reccrance!="NONE") or task.date > now)):
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
        self.props={}
        self.__internal_init__(rowData)
        self.internalId = fileName


    def __internal_init__(self, rowData):
        if rowData == None:
            raise Exception("row data cannot be null")
        taskRows = rowData.split("\n")
        mainRow = taskRows[0]
        if(len(taskRows) > 1):
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
        #     taskStr += "|"
        #     taskStr += self.notify
        taskStr += "|"
        taskStr += self.status
        return taskStr

    def toString(self):
        mainPart = self.get_main_part_as_string()

        if (len(self.props) >0):
            mainPart +="\n"
            for prop in self.props:
                mainPart +=prop + "=" + str(self.props[prop])
                mainPart += "|"

        return mainPart