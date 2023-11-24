import requests
import json
import os

from classes import Lesson, Schedule

def testLogin():
    # Test if session token is valid
    user_info = requests.get(api_url + "/Account/me", headers=header)
    if user_info.status_code != 200:
        raise Exception("INVALID_LOGIN_CREDENTIALS")

session_token: str = os.environ.get('SESSION_TOKEN') or ""
api_url = os.environ.get('API_URL') or 'https://kampus-sggw-api.azurewebsites.net/api'

if session_token == "":
    email = os.environ.get('API_EMAIL')
    password = os.environ.get('API_PASSWORD')

    if email == None or password == None:
        raise Exception("EMAIL_AND_PASSWORD_OR_SESSION_TOKEN_NOT_SET")
    r = requests.post(api_url + "/Tokens/login", json={"email": email, "password": password, "deviceToken": "EMAIL_SCRIPT"})

header = {"Authorization": "Bearer " + session_token}
testLogin()

def getSchedules():
    r = requests.get(api_url + "/Schedules", headers=header)
    if r.status_code != 200:
        raise Exception("ERROR_GETTING_SCHEDULES")
    return json.loads(r.text)

def deleteSchedule(id: str):
    r = requests.delete(api_url + "/Schedules/" + id, headers=header)
    if r.status_code != 200:
        raise Exception("ERROR_DELETING_SCHEDULE")
    return json.loads(r.text)

def deletePlanData():
    for schedule in getSchedules():
        deleteSchedule(schedule['id'])
