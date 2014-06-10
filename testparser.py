from unittest import TestCase
from parser import GoogleCalendarParser
from datetime import datetime

__author__ = 'sajith'


class MyTest(TestCase):
    def setUp(self):
        self.googleTaskFile = file("./googleagenda")
        self.googleParser = GoogleCalendarParser()

    def testParse(self):
        x = "12|3343|2342"
        v = x.split("|")[1:]
        z = "|".join([vv for vv in v])
        tasks = self.googleParser.parse(self.googleTaskFile)
        self.assertEqual(len(tasks),12)
