
from io import BytesIO
from math import e
from typing import List # For type hinting

class File:
    def __init__(self, name, content):
        self.name = name
        self.content = content

    def save(self, folder, name = None):
        import os
        if not os.path.isdir(folder):
            os.mkdir(folder)

        with open(folder + '/' + name, 'wb') as f:
            f.write(self.content)

    def __str__(self):
        return f"Name: {self.name}\nContent: {self.content}"

class EmailMessage:
    def __init__(self, subject, sender, recipient, date, body, attachments):
        self.subject = subject
        self.sender = sender
        self.recipient = recipient
        self.date = date
        self.body = body
        self.attachments: List[File] = attachments

    @classmethod
    def from_raw_email(cls, raw_email):
        def extract_body(parsed_email):
            body = ''
            for part in parsed_email.walk():
                body = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
                break

            return body

        def extract_attachments(parsed_email):
            attachments = []
            for part in parsed_email.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                filename = part.get_filename()
                if bool(filename):
                    attachments.append(File(filename, part.get_payload(decode=True)))
            return attachments

        import email
        raw_email = raw_email
        parsed_email = email.message_from_bytes(raw_email)
        subject = parsed_email['Subject']
        sender = parsed_email['From']
        recipient = parsed_email['To']
        date = parsed_email['Date']
        body = extract_body(parsed_email)
        attachments = extract_attachments(parsed_email)

        return cls(subject, sender, recipient, date, body, attachments)

    def save_attachments(self, folder):
        if len(self.attachments) == 0:
            return

        import os
        if not os.path.isdir(folder):
            os.mkdir(folder)

        for attachment in self.attachments:
            attachment.save(folder, attachment.name)

    def __str__(self):
        return f"Subject: {self.subject}\nFrom: {self.sender}\nTo: {self.recipient}\nDate: {self.date}\nBody: {self.body}\nAttachments: {self.attachments}"

class Schedule:
    def __init__(self, updateTime, faculty, field, degree, mode, year, semester, group, lessons):
        self.updateTime = updateTime
        self.faculty = faculty
        self.field = field
        self.degree = degree
        self.mode = mode
        self.year = year
        self.semester = semester
        self.lessons:List[Lesson] = lessons
        self.group = group

    @classmethod
    def getTimetablesFromFile(cls, filename:str):
        if filename.endswith('.txt'):
            with open(filename, 'r') as f:
                return [cls.getTimetableFromTXTData(f)]
        elif filename.endswith('.xlsx'):
            with open(filename, 'rb') as f:
                return cls.getTimetablesFromXLSXData(BytesIO(f.read()))
        else:
            return []



    @classmethod
    def getTimetablesFromXLSXData(cls, data:BytesIO):
        import pandas as pd
        from classes import Schedule, Lesson
        from typing import List # For type hinting

        def parse_sheet(data):
            schedules:List[Schedule] = []
            # Get sheet header
            schedule_data:str = data.iloc[0, 2].split(',') # type: ignore

            fieldOfStudent = schedule_data[0].strip()
            degree = schedule_data[1].strip()
            year = schedule_data[2].split('Rok')[1].strip()
            semester = schedule_data[3].split('Semestr')[1].strip()
            updateTime = "00:00"

            # Get Groups
            time_row = data.iloc[2]
            max_row = data.shape[0]
            for i in range(3, max_row):
                groupRow = data.iloc[i]
                schedule = parse_row(groupRow, time_row)

                # Skip division rows
                if schedule.group == '':
                    continue

                # Set rest of schedule data
                schedule.updateTime = updateTime
                schedule.field = fieldOfStudent
                schedule.degree = degree
                schedule.year = year
                schedule.semester = semester
                schedule.mode = "ZO"
                schedule.faculty = "WZIM"

                schedules.append(schedule)

            return schedules

        def parse_row(data, time_row):
            schedule = Schedule.empty()
            max_col = data.shape[0]-1
            groupName = str(data[1]).strip()
            # Skip header
            if groupName == "Grupy":
                return schedule

            schedule.group = groupName

            # Get day
            dayNum = 0
            dayText = str(data[0]).strip()
            if dayText.find('Piątek') != -1:
                dayNum = 5
            elif dayText.find('Sobota') != -1:
                dayNum = 6
            elif dayText.find('Niedziela') != -1:
                dayNum = 7

            # Get lessons
            lessons:List[Lesson] = []
            lesson:Lesson = Lesson.empty()
            lesson.dayNumber = dayNum
            lessonRaw = ""

            for j in range(2, max_col):
                lessonRaw = str(data[j])
                if lessonRaw == 'nan':
                    continue

                # Set start time
                lesson.timeStart = time_row[j]

                # Set end time and set j at the end of lesson
                k = j+1
                while(k+1 < max_col and data[k] != lessonRaw):
                    k += 1
                lesson.timeEnd = time_row.get(k)
                j = k

                # Parse lesson text
                lessonRaw = lessonRaw.split(',')
                lesson.name = lessonRaw[0].split('(')[0].strip()

                # Look for data
                for text in lessonRaw:
                    if text == 'WARUNEK':
                        continue
                    elif text.find('(') != -1:
                        lesson.type = text.split('(')[1].split(')')[0].strip()
                    # Look for location
                    elif text.find('s.') != -1:
                        lesson.location = text.split('s.')[1].strip()
                    # Look for building
                    elif text.find('b.') != -1:
                        lesson.building = text.split('b.')[1].split("]")[0].strip()
                    # Look for teacher (check if every word starts with capital letter and does not contain numbers)
                    else:
                        isTeacher = True # (probably)
                        for word in text.strip().split(' '):
                            if not word[0].isupper() or any(char.isdigit() for char in word):
                                isTeacher = False
                                break
                        if isTeacher:
                            lesson.teacher = text.strip()

                # Check if last line is not location, then it's comment
                if lessonRaw[-1].find(']') != -1:
                    lesson.comment = lessonRaw[-1].strip()


                lessons.append(lesson)
                lesson = Lesson.empty()

            schedule.lessons = lessons
            return schedule

        plans:List[Schedule] = []
        file = pd.ExcelFile(data)

        # For each sheet in the Excel file
        for sheet_name in file.sheet_names:
            sheetData = pd.read_excel(data, sheet_name=sheet_name, header=None)
            plans_for_sheet = parse_sheet(sheetData)
            plans.extend(plans_for_sheet)

        return plans


    @classmethod
    def getTimetableFromTXTData(cls, data):
        # 10.10.2023 22:34
        # WZIM, 2023, Jesień , ST, Inf, inż, R4, S7, gr1, ISI-1 ;
        lessons = []
        # Get update time
        updateTime = data.readline().strip() # 10.10.2023 22:34
        # Get name
        scheduleInfo = data.readline().strip().split(',')
        faculty = scheduleInfo[0].strip() # WZIM
        year = scheduleInfo[1].strip() # 2023
        mode = scheduleInfo[3].strip() # ST
        fieldOfStudent = scheduleInfo[4].strip() # Inf
        degree = scheduleInfo[5].strip() # inż
        year = scheduleInfo[6].strip().removeprefix('R').strip() # R4
        semester = scheduleInfo[7].strip().removeprefix('S').strip()# S7
        group = scheduleInfo[8].strip().removeprefix('gr').strip()# gr1

        # Divide file into blocks of lessons
        blocks = data.read().split('------------------------------------------------\n')
        # Iterate over blocks

        # ZJ_01
        # Sztuczna Inteligencja [Lab]
        # d1, 10:30-12:00
        # 3/18
        # Aleksandra Konopka
        # U: 8 tygodni (ostatnie zajęcia 45 minut krócej)
        for block in blocks:
            if block == '':
                continue
            elif block.find('end.') != -1:
                break
            # Divide block into lines
            lines = block.split('\n')

            # Parse text
            num = lines[0].strip()
            name = lines[1].split('[')[0].strip()
            type = lines[1].split('[')[1].split(']')[0].strip()
            day = lines[2].split(',')[0].strip().removeprefix('d').strip()
            timeStart = lines[2].split(',')[1].split('-')[0].strip()
            timeEnd = lines[2].split(',')[1].split('-')[1].strip()
            if lines[3] == "zdalne":
                room = 0
                building = 0
            elif lines[3].find('/') != -1:
                room = lines[3].split('/')[0].strip()
                building = lines[3].split('/')[1].strip()
            else:
                room = lines[3].split(',')[0].strip()
                building = lines[3].split(',')[1].strip()

            building = lines[3].split('/')[0].strip()
            teacher = lines[5].strip()
            comment = lines[6].removeprefix('U:').strip()

            # Create lesson object
            lesson = Lesson(num=num, name=name, type=type, day=day, timeStart=timeStart, timeEnd=timeEnd, room=room, floor=building, building=building, teacher=teacher, comment=comment, created='', updated='')
            # Add lesson to lessons list
            lessons.append(lesson)
        return cls(updateTime, faculty, fieldOfStudent, degree, mode, year, semester, group, lessons)

    @classmethod
    def empty(cls):
        return cls('', '', '', '', '', '', '', '', [])

    def __str__(self):
        return f"Update time: {self.updateTime}\nFaculty: {self.faculty}\nField: {self.field}\nDegree: {self.degree}\nMode: {self.mode}\nYear: {self.year}\nSemester: {self.semester}\nGroup: {self.group}\nLessons: {self.lessons}"

class Lesson:
    def __init__(self, num:int, created:str, updated:str, name:str, type:str, day, timeStart:str, timeEnd:str, room, floor, building, teacher:str, comment:str):
        self.num = num
        self.created = created
        self.updated = updated
        self.name = name
        self.type = type
        self.dayNumber = day
        self.timeStart = timeStart
        self.timeEnd = timeEnd
        self.location = room
        self.building = building
        self.teacher = teacher
        self.comment = comment

    @classmethod
    def empty(cls):
        return cls(num=0, created='', updated='', name='', type='', day='', timeStart='', timeEnd='', room='', floor='', building='', teacher='', comment='')
    def __str__(self):
        return f"{self.name}, {self.type}, {self.dayNumber}, {self.timeStart}, {self.timeEnd}, {self.location}, {self.teacher}"
