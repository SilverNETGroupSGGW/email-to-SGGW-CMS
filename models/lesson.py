import datetime
from enum import Enum
from lib.api_client import *
from lib.string_safety import secureString
from models.group import Group
from models.location import Location
from models.lecturer import Lecturer
from typing import Any, List
from datetime import time

class LessonType(Enum):
    LABORATORIES = "Laboratories"
    PracticalClasses = "PracticalClasses"
    LECTURE = "Lecture"
    UNKNOWN = "Unknown"

def strToType(string:str):
    if "lab" in string.lower():
        return LessonType.LABORATORIES
    elif "ćw" in string.lower():
        return LessonType.PracticalClasses
    elif "w" in string.lower():
        return LessonType.LECTURE
    else:
        return LessonType.UNKNOWN

class DayOfWeek(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

    @staticmethod
    def fromInt(day: int):
        if day == 2:
            return DayOfWeek.TUESDAY
        elif day == 3:
            return DayOfWeek.WEDNESDAY
        elif day == 4:
            return DayOfWeek.THURSDAY
        elif day == 5:
            return DayOfWeek.FRIDAY
        elif day == 6:
            return DayOfWeek.SATURDAY
        elif day == 7:
            return DayOfWeek.SUNDAY
        else:
            return DayOfWeek.MONDAY

class Lesson:
    def __init__(self, num:int=0, name:str="", groups:List[Group] = [], type:LessonType = LessonType.UNKNOWN,\
                 day:DayOfWeek=DayOfWeek.MONDAY, timeStart:time=time(), timeEnd:time=time(), location: None = None,\
                 lecturers:List[Lecturer]=[], comment:str=""):
        self.num = num
        self.groups: List[Group] = groups
        self.name = name
        self.type = type
        self.day:DayOfWeek = day
        self.startTime:time = timeStart
        self.endTime:time = timeEnd
        self.location:Location | None = location
        self.lecturers:List[Lecturer] = lecturers
        self.comment = comment

    def duration(self) -> time:
        dateDiffrence = datetime.datetime.combine(datetime.date.today(), self.endTime) - datetime.datetime.combine(datetime.date.today(), self.startTime)
        return time(dateDiffrence.seconds // 3600, (dateDiffrence.seconds // 60) % 60)

    def to_map(self, scheduleID: str, lecturerIDs: List[str], groupIDs: List[str], classroomID: str) -> dict[str, Any]:
        return {
            "name": secureString(self.name),
            "scheduleId": secureString(scheduleID),
            "type": self.type.name,
            "startTime": self.startTime.strftime("%H:%M:%S"),
            "dayOfWeek": self.day.name,
            "duration": self.duration().strftime("%H:%M:%S"),
            "lecturersIds": lecturerIDs,
            "groupsIds": groupIDs,
            "classroomId": classroomID,
            "comment": secureString(self.comment)
        }
    def __str__(self):
        return f"{self.name}, {self.type}, {self.day}, {self.startTime}, {self.endTime}, {self.location}, {self.lecturers}, {self.comment}"
