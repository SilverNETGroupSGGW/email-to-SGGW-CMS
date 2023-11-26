import datetime
from enum import Enum
from lib.string_safety import secureString
from models.location import Location
from models.lecturer import Lecturer
from typing import List
from datetime import time

class LessonType(Enum):
    LABORATORIES = "Laboratories"
    PRACTICAL_CLASSES = "PracticalClasses"
    LECTURE = "Lecture"
    UNKNOWN = "Unknown"

def strToType(string:str):
    if "lab" in string.lower():
        return LessonType.LABORATORIES
    elif "ćw" in string.lower():
        return LessonType.PRACTICAL_CLASSES
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
    def __init__(self, num:int=0, name:str="", type:LessonType = LessonType.UNKNOWN, day:DayOfWeek=DayOfWeek.MONDAY, timeStart:time=time(), timeEnd:time=time(), location:Location=Location(), lecturer:Lecturer=Lecturer(), comment:str=""):
        self.num = num
        self.name = name
        self.type = type
        self.day:DayOfWeek = day
        self.startTime:time = timeStart
        self.endTime:time = timeEnd
        self.location:Location = location
        self.lecturer:Lecturer = lecturer
        self.comment = comment

    def duration(self) -> time:
        dateDiffrence = datetime.datetime.combine(datetime.date.today(), self.endTime) - datetime.datetime.combine(datetime.date.today(), self.startTime)
        return time(dateDiffrence.seconds // 3600, (dateDiffrence.seconds // 60) % 60)


    def to_map(self, scheduleID: str, classroomID: str, groupIDs: List[str], lecturerIDs: List[str]):
        for groupID in groupIDs:
            groupID = secureString(groupID)

        for lecturerID in lecturerIDs:
            lecturerID = secureString(lecturerID)
        return {
            "name": secureString(self.name),
            "scheduleId": secureString(scheduleID),
            "type": self.type.name,
            "startTime": self.startTime.strftime("%H:%M:%S"),
            "dayOfWeek": self.day.name,
            "duration": self.duration().strftime("%H:%M:%S"),
            "lecturersIds": lecturerIDs,
            "groupsIds": groupIDs,
            "classroomId": secureString(classroomID),
            "comment": secureString(self.comment)
        }
    def __str__(self):
        return f"{self.name}, {self.type}, {self.day}, {self.startTime}, {self.endTime}, {self.location}, {self.lecturer}"
