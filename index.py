import copy
from dateutil import get_floor_time, get_time_as_str, countDays

__author__ = 'sajith'

import datetime
import shutil
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
            self.entries.append(Task(lines[0], filename))
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
                if normalizedEntryDate >= move_N_number_of_min_into_past and normalizedEntryDate <= overdueTime:
                    entry.dueIn = (overdueTime - normalizedEntryDate).seconds / 60
                    overdueTasks.append(entry)
                elif normalizedEntryDate > overdueTime and normalizedEntryDate <= soonStartTime:
                    entry.dueIn = (normalizedEntryDate - overdueTime).seconds / 60
                    startingSoonTasks.append(entry)
        return (overdueTasks, startingSoonTasks)

    def normalizeIfReccrentTask(self, task, now):
        # if task.reccrance != None and task.date < now and self.isItToday(task.date, now, task.reccrance) == True:
        if task.reccrance != None and task.date < now and self.isItToday(task.date, now, task.reccrance) == True:
            taskTime = task.date.time()
            return datetime.datetime.combine(now, taskTime)
        else:
            return task.date


    # def normalizeIfReccrentTask(self, task, now):
        # if task.reccrance != None and task.date < now:
        #     daysDiff = now.weekday() - task.date.weekday()
        #     taskTime = task.date.time()
        #     return datetime.datetime.combine(now + datetime.timedelta(days=daysDiff), taskTime)
        # else:
        #     return task.date

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
        pass

    def snooze(self, taskId):
        task = self.findTaskById(taskId)
        task.snoozed = 1

    def addTask(self, name, datetime=None, rec=None, notify=None):
        taskStr = name
        if (datetime != None):
            taskStr += "|"
            taskStr += datetime.strftime('%Y-%m-%d %H:%M')
        if (rec != None):
            taskStr += "|"
            taskStr += rec
        if (notify != None):
            taskStr += "|"
            taskStr += notify
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
        taskId.update(task.toString())
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
            # date = self.normalizeIfReccrentTask(task, now)
            daysBetweenTasks = countDays(now.weekday(),task.date.weekday())
            if (get_floor_time(task.date) == get_floor_time(now)):
                shallowCopyiedTask = copy.copy(task)
                shallowCopyiedTask.date = task.date
                todaysAgenda.append(shallowCopyiedTask)
                if(task.reccrance == "DAILY"):
                    shallowCopyiedTask = copy.copy(task)
                    shallowCopyiedTask.date=now + datetime.timedelta(days=1)
                    upcoming.append(shallowCopyiedTask)

            elif (task.reccrance == "DAILY" and task.date < now) or (daysBetweenTasks == 0 and task.reccrance == "WEEKLY" and task.date < now):
                    shallowCopyiedTask = copy.copy(task)
                    shallowCopyiedTask.date=now
                    todaysAgenda.append(shallowCopyiedTask)
                    shallowCopyiedTask1 = copy.copy(task)
                    shallowCopyiedTask1.date = now + datetime.timedelta(days=1)
                    upcoming.append(shallowCopyiedTask1)
            elif (daysBetweenTasks < 3 and task.date.weekday() > now.weekday()):
                    shallowCopyiedTask = copy.copy(task)
                    shallowCopyiedTask.date = now + datetime.timedelta(days=daysBetweenTasks)
                    upcoming.append(shallowCopyiedTask)

            # elif (get_floor_time(date) > get_floor_time(now) and get_floor_time(date) < get_floor_time(date + datetime.timedelta(days=3))):
            #     task.date = date
            #     upcoming.append(task)


        return todaysAgenda, upcoming

class Task:
    taskName = ""
    date = None
    reccrance = None
    notify = None
    status = None
    id = 0
    snoozed = 0
    dueIn = 0
    internalId = None

    def __init__(self, rowData, fileName=None):
        self.__internal_init__(rowData)
        self.internalId = fileName


    def __internal_init__(self, rowData):
        if rowData == None:
            raise Exception("row data cannot be null")
        rowData = rowData.rstrip('\n')
        parts = rowData.split("|", 6)
        self.id = int(parts[0])
        self.taskName = parts[1]
        partSize = len(parts)
        if (partSize > 3):
            dateTime = datetime.datetime.strptime(parts[2], '%Y-%m-%d %H:%M')
            self.date = dateTime
            self.hour = dateTime.time().hour
            self.min = dateTime.time().minute
            self.reccrance = parts[3]
            self.notify = parts[4]
            self.status = parts[5]
            if (partSize > 6):
                self.snoozed = int(parts[6])
        else:
            self.status = parts[2]

    def isOverdue(self):
        return self.date >= datetime.datetime.today() + datetime.timedelta(minutes=30)

    def toString(self):
        taskStr = str(self.id) + "|" + self.taskName
        if (self.date != None):
            taskStr += "|"
            taskStr += self.date.strftime('%Y-%m-%d %H:%M')
        if (self.reccrance != None):
            taskStr += "|"
            taskStr += self.reccrance
        if (self.notify != None):
            taskStr += "|"
            taskStr += self.notify
        taskStr += "|"
        taskStr += self.status
        return taskStr