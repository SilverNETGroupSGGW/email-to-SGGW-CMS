import requests
import json
from typing import List
import os
from models.location import Location
from models.lecturer import Lecturer
from models.lesson import Lesson
from models.group import Group
from models.schedule import Schedule

def testLogin():
    # Test if session token is valid
    user_info = requests.get(api_url + "/Account/me", headers=header)
    if user_info.status_code != 200:
        raise Exception("INVALID_LOGIN_CREDENTIALS")

session_token: str = os.environ.get("SESSION_TOKEN") or ""
api_url = os.environ.get("API_URL") or "https://kampus-sggw-api.azurewebsites.net/api"

if session_token == "":
    email = os.environ.get("API_USERNAME")
    password = os.environ.get("API_PASSWORD")

    if email == None or password == None:
        raise Exception("EMAIL_AND_PASSWORD_OR_SESSION_TOKEN_NOT_SET")
    r = requests.post(api_url + "/Tokens/login", json={"email": email, "password": password, "deviceToken": "EMAIL_SCRIPT"})
    if r.status_code != 200:
        raise Exception("INVALID_LOGIN_CREDENTIALS")
    session_token = json.loads(r.text)["accessToken"]

header = {"Authorization": "Bearer " + session_token}
testLogin()

def getClassrooms():
    r = requests.get(api_url + "/Classrooms", headers=header)
    if r.status_code != 200:
        raise Exception("ERROR_GETTING_CLASSROOMS")
    return json.loads(r.text)

def findClassroomID(location: Location | None):
    if location == None:
        location = Location(building="Zdalnie")
    for classroom in getClassrooms():
        if classroom["name"] == location.name() and classroom["building"] == location.building:
            return classroom["id"]
    raise Exception("ERROR_FINDING_CLASSROOM_ID")

def changeClassroom(id: str, classroom: Location):
    classroomJson = classroom.to_map()
    classroomJson["id"] = id
    with requests.put(api_url + "/Classrooms", headers=header, json=json.dumps(classroomJson)) as req:
        if req.status_code != 200:
            raise Exception("ERROR_CHANGING_CLASSROOM")

def addClassroom(classroom: Location| None):
    if classroom == None:
        classroomJson = {
        "name": "",
        "building": "Zdalnie"
        }
    else:
        classroomJson = classroom.to_map()
    classroomID = requests.post(api_url + "/Classrooms", headers=header, json=classroomJson)
    if classroomID.status_code != 200:
        raise Exception("ERROR_POSTING_CLASSROOM")
    classroomID = findClassroomID(classroom)
    return classroomID

def deleteClassroom(id: str):
    with requests.delete(api_url + "/Classrooms/" + id, headers=header) as req:
        if req.status_code != 200:
            raise Exception("ERROR_DELETING_CLASSROOM")

def getGroups():
    r = requests.get(api_url + "/Groups", headers=header)
    if r.status_code != 200:
        raise Exception("ERROR_GETTING_GROUPS")
    return json.loads(r.text)

def findGroupID(group: Group, scheduleID: str) -> str:
    for groupJSON in getGroups():
        if groupJSON["name"] == group.name and groupJSON["scheduleId"] == scheduleID:
            return groupJSON["id"]
    raise Exception("ERROR_FINDING_GROUP_ID")

def changeGroup(id: str, group: Group, scheduleID: str):
    groupJson = group.to_map(scheduleID=scheduleID)
    groupJson["id"] = id
    with requests.put(api_url + "/Groups", headers=header, json=groupJson) as req:
        if req.status_code != 200:
            raise Exception("ERROR_CHANGING_GROUP")

def addGroup(group: Group, scheduleID: str):
    groupID = requests.post(api_url + "/Groups", headers=header, json=group.to_map(scheduleID=scheduleID))
    if groupID.status_code != 200:
        raise Exception("ERROR_POSTING_GROUP")
    return findGroupID(group, scheduleID=scheduleID)

def deleteGroup(id: str):
    with requests.delete(api_url + "/Groups/" + id, headers=header) as req:
        if req.status_code != 200:
            raise Exception("ERROR_DELETING_GROUP")

def getSchedules():
    r = requests.get(api_url + "/Schedules", headers=header)
    if r.status_code != 200:
        raise Exception("ERROR_GETTING_SCHEDULES")
    return json.loads(r.text)

def changeSchedule(id: str, schedule: Schedule):
    scheduleJson = schedule.to_map()
    scheduleJson["id"] = id
    with requests.put(api_url + "/Schedules", headers=header, json=json.dumps(scheduleJson)) as req:
        if req.status_code != 200:
            raise Exception("ERROR_CHANGING_SCHEDULE")

def findScheduleID(schedule: Schedule):
    for scheduleJSON in getSchedules():
        if scheduleJSON["name"] == schedule.name():
            return scheduleJSON["id"]
    raise Exception("ERROR_FINDING_SCHEDULE_ID")

def addSchedule(schedule: Schedule):
    scheduleID = requests.post(api_url + "/Schedules", headers=header, json=schedule.to_map())
    if scheduleID.status_code != 200:
        raise Exception("ERROR_POSTING_SCHEDULE")

    scheduleID = findScheduleID(schedule)
    return scheduleID

def getLecturers():
    r = requests.get(api_url + "/Lecturers", headers=header)
    if r.status_code != 200:
        raise Exception("ERROR_GETTING_LECTURERS")
    return json.loads(r.text)

def changeLecturer(id: str, lecturer: Lecturer):
    lecturerJson = lecturer.to_map()
    lecturerJson["id"] = id
    with requests.put(api_url + "/Lecturers", headers=header, json=lecturerJson) as req:
        if req.status_code != 200:
            raise Exception("ERROR_CHANGING_LECTURER")

def findLecturerID(lecturer: Lecturer) -> str:
    for lecturerJSON in getLecturers():
        if lecturer.name in lecturerJSON["firstName"] and lecturer.surname in lecturerJSON["surname"]:
            return lecturerJSON["id"]
        # If existing name or surname is longer than new one
        elif lecturerJSON["firstName"] in lecturer.name and lecturerJSON["surname"] in lecturer.surname:
            changeLecturer(lecturerJSON["id"], lecturer)
            return lecturerJSON["id"]
    raise Exception("ERROR_FINDING_LECTURER_ID")

def addLecturer(lecturer: Lecturer):
    lecturerID = requests.post(api_url + "/Lecturers", headers=header, json=lecturer.to_map())
    if lecturerID.status_code != 200:
        raise Exception("ERROR_POSTING_LECTURER")
    lecturerID = findLecturerID(lecturer)
    return lecturerID

def deleteLecturer(id: str):
    with requests.delete(api_url + "/Lecturers/" + id, headers=header) as req:
        if req.status_code != 200:
            raise Exception("ERROR_DELETING_LECTURER")

def getLessons():
    r = requests.get(api_url + "/Lessons", headers=header)
    if r.status_code != 200:
        raise Exception("ERROR_GETTING_LESSONS")
    return json.loads(r.text)

def deleteLesson(id: str):
    with requests.delete(api_url + "/Lessons/" + id, headers=header) as req:
        if req.status_code != 200:
            raise Exception("ERROR_DELETING_LESSON")

def findLessonID(lesson: Lesson, scheduleID: str):
    for lessonJSON in getLessons():
        if lessonJSON["name"] == lesson.name \
            and lessonJSON["scheduleId"] == scheduleID \
                and lessonJSON["type"] == lesson.type.name \
                    and lessonJSON["startTime"] == lesson.startTime.strftime("%H:%M:%S") \
                        and lessonJSON["dayOfWeek"] == lesson.day.name \
                            and lessonJSON["duration"] == lesson.duration().strftime("%H:%M:%S") \
                                and lessonJSON["comment"] == lesson.comment \
                                    and lessonJSON["classroomId"] == findClassroomID(lesson.location):
            return lessonJSON["id"]
    raise Exception("ERROR_FINDING_LESSON_ID")

def addLesson(lesson: Lesson, scheduleID: str):
    lessonJson = lesson.to_map(scheduleID=scheduleID, lecturerIDs=[findLecturerID(lecturer) for lecturer in lesson.lecturers], groupIDs=[findGroupID(group, scheduleID) for group in lesson.groups], classroomID=findClassroomID(lesson.location))
    lessonID = requests.post(api_url + "/Lessons", headers=header, json=lessonJson)
    if lessonID.status_code != 200:
        raise Exception("ERROR_POSTING_LESSON")
    return lessonID

def addGroupToLesson(lessonID: str, groupID: str):
    lessonJson = requests.get(api_url + "/Lessons/" + lessonID, headers=header)
    if lessonJson.status_code != 200:
        raise Exception("ERROR_GETTING_LESSON")
    lessonJson = json.loads(lessonJson.text)
    lessonJson["groupsIds"].append(groupID)
    with requests.put(api_url + "/Lessons", headers=header, json=json.dumps(lessonJson)) as req:
        if req.status_code != 200:
            raise Exception("ERROR_CHANGING_LESSON")

def changePlanData(schedules: List[Schedule]):
    from lib.logger import logger

    # Update schedules
    for schedule in schedules:
        logger.info("")
        logger.info("Updating plan data for")
        logger.info(schedule.name())
        logger.info("Degree " + schedule.degree.name)

        # Check if schedule exists
        try:
            scheduleID = findScheduleID(schedule)
        except:
            scheduleID = addSchedule(schedule)

        # Check if groups exists
        for group in schedule.groups:
            try:
                findGroupID(group, scheduleID)
            except:
                addGroup(group, scheduleID)

        # Remove lessons for this schedule
        for lessonJson in getLessons():
            if lessonJson["scheduleId"] == scheduleID:
                deleteLesson(lessonJson["id"])

        # Add back lessons for this schedule
        for lesson in schedule.lessons:
            # Check if classroom exists
            try:
                findClassroomID(lesson.location)
            except:
                addClassroom(lesson.location)

            # Check if lecturer exists
            for lecturer in lesson.lecturers:
                try:
                    findLecturerID(lecturer)
                except:
                    addLecturer(lecturer)
            try:
                lessonID = findLessonID(lesson, scheduleID)
            except:
                addLesson(lesson, scheduleID)
                continue

            for group in lesson.groups:
                addGroupToLesson(lessonID, findGroupID(group, scheduleID))