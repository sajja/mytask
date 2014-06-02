__author__ = 'sajith'
from index import Index, Task
import unittest
import datetime
import hashlib
import os


class MyTest(unittest.TestCase):
    def setUp(self):


        for fileToRemove in os.listdir(".task"):
            file_path = os.path.join(".task", fileToRemove)
            if os.path.isfile(file_path) and fileToRemove != "key":
                os.unlink(file_path)

        today = datetime.datetime.today().date()
        self.__create_initial_task__("1|Test1|PENDING", "1")
        self.__create_initial_task__("2|Test2|DONE", "2")
        self.__create_initial_task__("3|Test3|2014-05-14 15:30|DAILY|NOTIFY|PENDING", "3")
        self.__create_initial_task__("4|Test4|2014-05-14 16:30|NONE|NOTIFY|PENDING", "4")
        self.__create_initial_task__(Task("5|Today task1|" + today.strftime('%Y-%m-%d %H:%M') + "|NONE|NOTIFY|PENDING",
                                          self.__calculate_file_name__("5|Today task1|" + today.strftime(
                                              '%Y-%m-%d %H:%M') + "|NONE|NOTIFY|PENDING")).toString(), "5")

        self.index = Index()

    def test_list_all_pending(self):
        today = datetime.datetime.today()

        taskWithDate, taskWithoutDate = self.index.listAll()

        self.assertEqual(len(taskWithoutDate), 1)
        self.assertEqual(len(taskWithDate), 3)
        self.assertTask(taskWithoutDate, "Test1", "PENDING", None, None, ignoreDates=True)
        self.assertTask(taskWithDate, "Test3", "PENDING",
                        datetime.datetime.strptime('2014-05-14 15:30', '%Y-%m-%d %H:%M'), 'DAILY')
        self.assertTask(taskWithDate, "Test4", "PENDING",
                        datetime.datetime.strptime('2014-05-14 16:30', '%Y-%m-%d %H:%M'), 'NONE')
        self.assertTask(taskWithDate, "Today task1", "PENDING", today.date(), 'NONE', True)


    def test_list_all(self):
        today = datetime.datetime.today()

        taskWithDate, taskWithoutDate = self.index.listAll(status=None)

        self.assertEqual(len(taskWithoutDate), 2)
        self.assertEqual(len(taskWithDate), 3)
        self.assertTask(taskWithoutDate, "Test1", "PENDING", None, None, ignoreDates=True)
        self.assertTask(taskWithoutDate, "Test2", "DONE", None, None, ignoreDates=True)
        self.assertTask(taskWithDate, "Test3", "PENDING",
                        datetime.datetime.strptime('2014-05-14 15:30', '%Y-%m-%d %H:%M'),
                        'DAILY')
        self.assertTask(taskWithDate, "Test4", "PENDING",
                        datetime.datetime.strptime('2014-05-14 16:30', '%Y-%m-%d %H:%M'),
                        'NONE')
        self.assertTask(taskWithDate, "Today task1", "PENDING", today.date(), 'NONE', True)


    def test_todays_tasks(self):
        today = datetime.datetime.today().date()
        todayTasks = self.index.listTodayTasks()
        self.assertEqual(len(todayTasks), 1)
        self.assertTask(todayTasks, "Today task1", "PENDING", today, 'NONE', True)

    def test_pendig_reccurent_tasks_needs_notifying(self):
        today = datetime.datetime.today()
        yesterday_5_min_future = today + datetime.timedelta(days=-1) + datetime.timedelta(minutes=5)
        twodays_ago_10_min_future = today + datetime.timedelta(days=-2) + datetime.timedelta(minutes=10)
        yesterday_40_min_future = today + datetime.timedelta(days=-1) + datetime.timedelta(minutes=20)

        self.addTask(6, "yesterday task which starts in 5 min", "PENDING",
                     yesterday_5_min_future.strftime('%Y-%m-%d %H:%M'), "DAILY",
                     "NOTIFY")
        self.addTask(6, "day before yesterday task which starts in 10 min", "PENDING",
                     twodays_ago_10_min_future.strftime('%Y-%m-%d %H:%M'), "DAILY",
                     "NOTIFY")
        self.addTask(8, "yesterday task which starts in 40 min", "PENDING",
                     yesterday_40_min_future.strftime('%Y-%m-%d %H:%M'), "DAILY",
                     "NOTIFY")

        todayTime = today.time()
        yestedayTime = yesterday_5_min_future.time()
        print(datetime.datetime.combine(today, yestedayTime) - datetime.datetime.combine(today, todayTime) )
        print(datetime.datetime.combine(today, todayTime) - datetime.datetime.combine(today, yestedayTime) )

    def testAgenda(self):
        today = datetime.datetime.today()
        yesterday = today + datetime.timedelta(days=-1) + datetime.timedelta(minutes=5)
        twodays_ago = today + datetime.timedelta(days=-2) + datetime.timedelta(minutes=10)
        tomorrow = today + datetime.timedelta(days=1) + datetime.timedelta(minutes=20)
        lastWeekSameDay = today + datetime.timedelta(days=-7) + datetime.timedelta(minutes=20)
        lastWeekNotSameDay = today + datetime.timedelta(days=-8) + datetime.timedelta(minutes=20)
        lastWeekTwoDaysFromNow = today + datetime.timedelta(days=-5) + datetime.timedelta(minutes=20)
        lastWeekFourDaysFromNow = today + datetime.timedelta(days=-11)+ datetime.timedelta(minutes=20)

        todayDailyRecTask = self.createTask(111, today.strftime('%Y-%m-%d %H:%M'), "t1", "1", "DAILY", 0, "PENDING")
        yesterdayDailyRecTask = self.createTask(112, yesterday.strftime('%Y-%m-%d %H:%M'), "t2", "1", "DAILY", 0,
                                                "PENDING")
        tomorrowDailyRecTask = self.createTask(113, tomorrow.strftime('%Y-%m-%d %H:%M'), "t3", "1", "DAILY", 0,
                                               "PENDING")
        lastWeekNotRecTask1 = self.createTask(113, lastWeekSameDay.strftime('%Y-%m-%d %H:%M'), "t4", "1", "WEEKLY", 0,
                                              "PENDING")
        lastWeekNotRecTask2 = self.createTask(113, lastWeekNotSameDay.strftime('%Y-%m-%d %H:%M'), "t5", "1", "WEEKLY",
                                              0, "PENDING")
        lastWeekNotRecTask3 = self.createTask(113, lastWeekTwoDaysFromNow.strftime('%Y-%m-%d %H:%M'), "t6", "1",
                                              "WEEKLY", 0, "PENDING")
        lastWeekTask4= self.createTask(113, lastWeekFourDaysFromNow.strftime('%Y-%m-%d %H:%M'), "t7", "1",
                                              "WEEKLY", 0, "PENDING")

        taskList = [todayDailyRecTask.toString(), yesterdayDailyRecTask.toString(), todayDailyRecTask.toString(),
                    lastWeekNotRecTask1.toString(), lastWeekNotRecTask2.toString(), tomorrowDailyRecTask.toString(),
                    lastWeekNotRecTask3.toString()
            # ,lastWeekTask4.toString()
        ]
        self.__create__initial_tasks__(taskList)

        self.index = Index()
        todayTasks, upComing = self.index.agenda()
        self.assertEqual(len(todayTasks), 5)
        self.assertTask(todayTasks, "t1", "PENDING", today, rec="DAILY")
        self.assertTask(todayTasks, "Today task1", "PENDING", today.date(), rec="NONE", roundDates=True)
        self.assertTask(todayTasks, "t2", "PENDING", today.date(), rec="DAILY", roundDates=True)
        self.assertTask(todayTasks, "t4", "PENDING", today.date(), rec="WEEKLY", roundDates=True)
        self.assertTask(todayTasks, "Test3", "PENDING", today.date(), rec="DAILY", roundDates=True)

        self.assertEqual(len(upComing), 6)
        self.assertTask(upComing, "t1", "PENDING", rec="DAILY", ignoreDates=True)
        self.assertTask(upComing, "t2", "PENDING", rec="DAILY", ignoreDates=True)
        self.assertTask(upComing, "Test3", "PENDING", rec="DAILY", ignoreDates=True)
        self.assertTask(upComing, "t3", "PENDING", rec="DAILY", ignoreDates=True)
        self.assertTask(upComing, "t4", "PENDING", rec="WEEKLY", ignoreDates=True)
        self.assertTask(upComing, "t6", "PENDING", rec="WEEKLY", ignoreDates=True)


    def testNormalize(self):
        today = datetime.datetime.today()
        yesterday_5_min_future = today + datetime.timedelta(days=-1) + datetime.timedelta(minutes=5)
        twodays_ago_10_min_future = today + datetime.timedelta(days=-2) + datetime.timedelta(minutes=10)
        yesterday_40_min_future = today + datetime.timedelta(days=-1) + datetime.timedelta(minutes=20)
        tomorrow = today + datetime.timedelta(days=1) + datetime.timedelta(minutes=20)
        lastWeekSameDay = today + datetime.timedelta(days=-7) + datetime.timedelta(minutes=20)
        lastWeekNotSameDay = today + datetime.timedelta(days=-8) + datetime.timedelta(minutes=20)

        task1 = self.createTask(111, yesterday_5_min_future.strftime('%Y-%m-%d %H:%M'), "t1", "1", "DAILY", 0,
                                "PENDING")
        task2 = self.createTask(112, twodays_ago_10_min_future.strftime('%Y-%m-%d %H:%M'), "t1", "1", "DAILY", 0,
                                "PENDING")
        task3 = self.createTask(113, yesterday_40_min_future.strftime('%Y-%m-%d %H:%M'), "t1", "1", "DAILY", 0,
                                "PENDING")
        task4 = self.createTask(114, tomorrow.strftime('%Y-%m-%d %H:%M'), "t1", "1", "DAILY", 0, "PENDING")
        task5 = self.createTask(115, lastWeekNotSameDay.strftime('%Y-%m-%d %H:%M'), "t1", "1", "WEEKLY", 0, "PENDING")
        task6 = self.createTask(116, lastWeekSameDay.strftime('%Y-%m-%d %H:%M'), "t1", "1", "WEEKLY", 0, "PENDING")

        t1Date = self.index.normalizeIfReccrentTask(task1, today)
        t2Date = self.index.normalizeIfReccrentTask(task2, today)
        t3Date = self.index.normalizeIfReccrentTask(task3, today)
        t4Date = self.index.normalizeIfReccrentTask(task4, today)
        t5Date = self.index.normalizeIfReccrentTask(task5, today)
        t6Date = self.index.normalizeIfReccrentTask(task6, today)

        self.assertEqual(t1Date.date(), today.date())
        self.assertEqual(t2Date.date(), today.date())
        self.assertEqual(t3Date.date(), today.date())
        self.assertNotEqual(t4Date.date(), today.date())
        self.assertNotEqual(t5Date.date(), today.date())
        self.assertEqual(t6Date.date(), today.date())

    def test_daily_reccurence(self):
        today = datetime.datetime.today()
        yesterday_10_min_future = today + datetime.timedelta(minutes=10) + datetime.timedelta(days=-1)
        day_before_yesterday_10_min_past = today + datetime.timedelta(minutes=-10) + datetime.timedelta(days=-1)
        self.addTask(6, "yesterday overdue", "PENDING", day_before_yesterday_10_min_past.strftime('%Y-%m-%d %H:%M'),
                     "DAILY", "NOTIFY")
        self.addTask(7, "yesterday overdue no rec", "PENDING",
                     day_before_yesterday_10_min_past.strftime('%Y-%m-%d %H:%M'), "NONE", "NOTIFY")
        self.addTask(8, "yesterday future", "PENDING", yesterday_10_min_future.strftime('%Y-%m-%d %H:%M'), "DAILY",
                     "NOTIFY")
        self.addTask(9, "yesterday future no rec", "PENDING", yesterday_10_min_future.strftime('%Y-%m-%d %H:%M'),
                     "NONE", "NOTIFY")

        notifiedTasks = self.index.listNotificationsPendingTasks(15)
        self.assertEqual(len(notifiedTasks[0]), 1)
        self.assertEqual(len(notifiedTasks[1]), 1)

    def test_list_pending_notifications(self):
        today = datetime.datetime.today()
        today_10_min_future = today + datetime.timedelta(minutes=10)
        today_15_min_future = today + datetime.timedelta(minutes=15)
        today_20_min_future = today + datetime.timedelta(minutes=20)
        today_30_min_future = today + datetime.timedelta(minutes=30)
        today_1_hour_future = today + datetime.timedelta(hours=1)

        self.addTask(6, "task statring in 10 min", "PENDING", today_10_min_future.strftime('%Y-%m-%d %H:%M'), "NONE",
                     "NOTIFY")
        self.addTask(7, "task statring in 15 min", "PENDING", today_15_min_future.strftime('%Y-%m-%d %H:%M'), "NONE",
                     "NOTIFY")
        self.addTask(8, "task statring in 20 min", "PENDING", today_20_min_future.strftime('%Y-%m-%d %H:%M'), "NONE",
                     "NOTIFY")
        self.addTask(9, "task statring in 30 min", "PENDING", today_30_min_future.strftime('%Y-%m-%d %H:%M'), "NONE",
                     "NOTIFY")
        self.addTask(10, "task statring in one hour", "PENDING", today_1_hour_future.strftime('%Y-%m-%d %H:%M'), "NONE",
                     "NOTIFY")
        self.addTask(11, "task statring in 10 min but snoozed", "PENDING",
                     today_10_min_future.strftime('%Y-%m-%d %H:%M'), "NONE",
                     "NOTIFY", 1)
        todayTasks = self.index.listTodayTasks()
        self.assertEqual(len(todayTasks), 7)
        taskStartsIn15Min = self.index.listNotificationsPendingTasks(15)
        #snooze not implemented yet
        self.assertEqual(len(taskStartsIn15Min[0]), 0)
        self.assertEqual(len(taskStartsIn15Min[1]), 3)


    # def test_pending_task_could_be_snoozed(self):
    #     today = datetime.datetime.today()
    #     today_10_min_future = today + datetime.timedelta(minutes=10)
    #
    #     self.addTask(6, "task statring in 10 min", "PENDING", today_10_min_future.strftime('%Y-%m-%d %H:%M'), "NONE",
    #                  "NOTIFY")
    #     todayTasks = self.index.listNotificationsPendingTasks()
    #     self.assertEqual(len(todayTasks), 1)
    #     self.index.snooze(6)
    #     todayTasks = self.index.listNotificationsPendingTasks()
    #     self.assertEqual(len(todayTasks), 0)


    def test_overdue_task(self):
        now = datetime.datetime.now()
        overdueBy31Min = now - datetime.timedelta(minutes=-32)
        overdueTaskBy32 = Task(
            "1|od1|" + overdueBy31Min.strftime('%Y-%m-%d %H:%M') + "|NONE|NOTIFY|PENDING",
            self.__calculate_file_name__("1|od1|" + overdueBy31Min.strftime('%Y-%m-%d %H:%M') + "|NONE|NOTIFY|PENDING"))
        overdueBy29Min = now - datetime.timedelta(minutes=-28)
        overdueTaskBy28 = Task(
            "3|od1|" + overdueBy29Min.strftime('%Y-%m-%d %H:%M') + "|NONE|NOTIFY|PENDING",
            self.__calculate_file_name__("3|od1|" + overdueBy29Min.strftime('%Y-%m-%d %H:%M') + "|NONE|NOTIFY|PENDING"))

        self.assertEqual(overdueTaskBy32.isOverdue(), True)
        self.assertEqual(overdueTaskBy28.isOverdue(), False)

    def __calculate_file_name__(self, data):
        fileHash = hashlib.sha1()
        fileHash.update(data)
        return fileHash.hexdigest()

    def test_add_task_long(self):
        now = datetime.datetime.now()
        taskWithDate, taskWithoutDate = self.index.listAll()
        self.assertEqual(len(taskWithDate), 3)
        self.assertEqual(len(taskWithoutDate), 1)
        self.index.addTask("new task", now, "NONE", "NONE")
        taskWithDate, taskWithoutDate = self.index.listAll()
        self.assertEqual(len(taskWithDate), 4)
        self.assertTask(taskWithDate, "new task", "PENDING", now.date(), "NONE", True)

    def test_get_new_id(self):
        task1 = self.index.addTask("task1")
        task2 = self.index.addTask("task2")
        self.assertEqual(task1.id, (task2.id - 1))


    def test_add_task_short(self):
        now = datetime.datetime.now()
        taskWithDate, taskWithoutDate = self.index.listAll()
        self.assertEqual(len(taskWithDate), 3)
        self.assertEqual(len(taskWithoutDate), 1)
        self.index.addTask("new task", None, None, None)
        taskWithDate, taskWithoutDate = Index().listAll()
        self.assertEqual(len(taskWithoutDate), 2)
        self.assertTask(taskWithoutDate, "new task", "PENDING", None, None, ignoreDates=True)


    def test_mark_task_done(self):
        now = datetime.datetime.now()
        newTask = self.index.addTask("new task", now, "NONE", "NONE")
        taskWithDate, taskWithoutDates = self.index.listAll()
        self.assertEqual(len(taskWithDate), 4)
        self.assertEqual(len(taskWithoutDates), 1)
        updatedTask = self.index.markTaskComplete(newTask.id)
        self.assertEqual(updatedTask.status, "DONE")
        index = Index()
        deltedTask = index.findTaskById(updatedTask.id)
        self.assertIsNone(deltedTask)

    def test_delete(self):
        taskWithDates, taskWithoutDates = self.index.listAll()
        oldCount = len(taskWithoutDates)
        taskToBeDeleted = taskWithoutDates[0].id
        self.index.deleteTask(self.index.findTaskById(taskToBeDeleted))

        taskWithDates, taskWithoutDates = self.index.listAll()
        self.assertEqual(oldCount - 1, len(taskWithoutDates))
        deletedTask = self.index.findTaskById(taskToBeDeleted)
        self.assertEqual(deletedTask, None)


    def assertTask(self, taskList, name, status, date=None, rec=None, roundDates=False, ignoreDates=False):
        match = False
        for task in taskList:
            if (task.taskName == name and task.status == status and task.reccrance == rec ):
                if (ignoreDates):
                    match = True
                    break
                elif (roundDates == True and task.date != None and task.date.date() == date):
                    match = True
                    break
                else:
                    if hasattr(date, "second") and task.date == date.replace(second=0, microsecond=0):
                        match = True
                        break
        self.assertTrue(match == True, "Unable to find a task with given values")

    def createTask(self, id, datetime, name, notify, rec, snoozed, status):
        return Task(
            str(id) + "|" + name + "|" + datetime + "|" + rec + "|" + notify + "|" + status + "|" + str(snoozed),
            self.__calculate_file_name__(
                str(id) + "|" + name + "|" + datetime + "|" + rec + "|" + notify + "|" + status + "|" + str(snoozed)))

    def addTask(self, id, name, status, datetime, rec, notify, snoozed=0):
        self.index.entries.append(
            self.createTask(id, datetime, name, notify, rec, snoozed, status))

    def __create__initial_tasks__(self, tasks):
        i = 1000
        for task in tasks:
            self.__create_initial_task__(task, str(i))
            i += 1

    def __create_initial_task__(self, task, id):
        taskId = hashlib.sha1()
        taskId.update(task)
        todofile = file(".task/" + taskId.hexdigest(), "w")
        todofile.write(task)
        todofile.flush()
        todofile.close()
        keyFile = file('.task/key', "w")
        keyFile.write(id)
        keyFile.flush()
        keyFile.close()



