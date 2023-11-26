from io import BytesIO
from typing import List # For type hinting
from datetime import datetime
from lib.string_safety import secureString
from models.lesson import DayOfWeek, Lesson, strToType
from models.group import Group

def dayToDayNum(day: str):
    if day == "Poniedziałek":
        return 1
    elif day == "Wtorek":
        return 2
    elif day == "Środa":
        return 3
    elif day == "Czwartek":
        return 4
    elif day == "Piątek":
        return 5
    elif day == "Sobota":
        return 6
    elif day == "Niedziela":
        return 7
    else:
        return 0

class Schedule:
    def __init__(self, faculty:str="", field:str="", degree:str="", mode:str="", year:int=0, semester:int=0, group:Group=Group(), lessons:List[Lesson]=[]):
        if lessons == []:
            lessons = []
        self.faculty = faculty
        self.field = field
        self.degree = degree
        self.mode = mode
        self.year = year
        self.semester = semester
        self.group:Group = group
        self.lessons: List[Lesson] = lessons

    def name(self):
        return self.field + " R" + str(self.year) + "S" + str(self.semester)


    @classmethod
    def get_timetables_from_xlsx_data_openpyxl(cls, data: BytesIO):
        from openpyxl import load_workbook, cell
        from openpyxl.worksheet.worksheet import Worksheet
        from openpyxl.cell.cell import Cell, MergedCell

        def parse_sheet(sheet: Worksheet):
            schedules:List[Schedule] = []
            schedule_data = str(sheet.cell(row=1, column=3).value).split(sep=",")

            fieldOfStudent = schedule_data[0].strip()
            degree = schedule_data[1].strip()
            year = schedule_data[2].split("Rok")[1].strip()
            semester = schedule_data[3].split("Semestr")[1].strip()

            time_row:tuple[Cell,...] = ()
            i:int = 2
            while sheet[i+1][1].value != None and sheet[i+1][1].value != "":
                i += 1
                # Check if this is time row
                if sheet[i][1].value == "Grupy":
                    time_row = sheet[i]
                    continue
                group_row = sheet[i]
                schedule = parse_row(group_row, time_row)

                if schedule.group == Group():
                    continue

                schedule.field = fieldOfStudent
                schedule.degree = degree
                schedule.year = year
                schedule.semester = semester
                schedule.mode = "ZO"
                schedule.faculty = "WZIM"

                # Check if schedule already exists
                skip = False
                for existing_schedule in schedules:
                    if existing_schedule.name() == schedule.name():
                        if existing_schedule.group.name == schedule.group.name:
                            existing_schedule.lessons.extend(schedule.lessons)
                            skip = True
                            break
                if not skip:
                    schedules.append(schedule)


            return schedules

        def parse_row(row:tuple[Cell | MergedCell,...], time_row:tuple[Cell,...]):
            schedule = Schedule()
            max_col = len(row)
            groupName = str(row[1].value).strip()

            if groupName == "Grupy":
                return schedule

            schedule.group = Group(groupName)

            dayWithInfo = str(row[0].value).strip()
            if "Piątek" in dayWithInfo:
                day = DayOfWeek.FRIDAY
            elif "Sobota" in dayWithInfo:
                day = DayOfWeek.SATURDAY
            elif "Niedziela" in dayWithInfo:
                day = DayOfWeek.SUNDAY
            else:
                day = DayOfWeek.MONDAY

            for j in range(2, max_col):
                lesson = Lesson(day=day)

                lessonRaw = str(row[j].value)
                if lessonRaw == "None":
                    continue

                lesson.startTime = time_row[j].value

                # Set j at the next Cell (not MergedCell)
                while(j+1 < max_col):
                    # If next cell is MergedCell, skip it
                    if type(row[j+1]) == cell.MergedCell:
                        j += 1
                    else:
                        break

                lesson.endTime = time_row[j].value

                lessonRaw = lessonRaw.split(",")
                lesson.name = lessonRaw[0].split("(")[0].strip()

                for text in lessonRaw:
                    if text == "WARUNEK":
                        continue
                    elif "(" in text:
                        lesson.type = strToType(string=text.split("(")[1].split(")")[0].strip())
                    elif "s." in text:
                        if "/" in text:
                            lesson.location.floor = int(text.split("s.")[1].split("/")[0].strip())
                            lesson.location.classroom = text.split("s.")[1].split("/")[1].strip()
                        else:
                            lesson.location.classroom = text.split("s.")[1].strip()
                    elif "b." in text:
                        lesson.location.building = text.split("b.")[1].split("]")[0].strip()
                    else:
                        isTeacher = True
                        for word in text.strip().split(" "):
                            if not word[0].isupper() or any(char.isdigit() for char in word):
                                isTeacher = False
                                break
                        if isTeacher:
                            teacherData = text.strip().split(" ")
                            lesson.lecturer.name = " ".join(teacherData[0:-2])
                            lesson.lecturer.surname = teacherData[-1].strip()

                if not "]" in lessonRaw[-1] and len(lessonRaw) > 1:
                    lesson.comment = lessonRaw[-1].strip().strip(".")

                schedule.lessons.append(lesson)
            return schedule

        plans:List[Schedule] = []
        workbook = load_workbook(data, data_only=True)

        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            plans_for_sheet = parse_sheet(sheet)
            plans.extend(plans_for_sheet)
        return plans

    @classmethod
    def get_timetable_from_txt_data(cls, data: List[str]):
        # 10.10.2023 22:34
        # WZIM, 2023, Jesień , ST, Inf, inż, R4, S7, gr1, ISI-1 ;
        lessons:List[Lesson] = []
        schedule = Schedule()
        # Get name
        scheduleInfo = data[1].strip().split(",")
        schedule.faculty = scheduleInfo[0].strip() # WZIM
        schedule.year = scheduleInfo[1].strip() # 2023
        schedule.mode = scheduleInfo[3].strip() # ST
        schedule.field = scheduleInfo[4].strip() # Inf
        if schedule.field == "Inf":
            schedule.field = "Informatyka"
        schedule.degree = scheduleInfo[5].strip() # inż
        schedule.year = int(scheduleInfo[6].strip().removeprefix("R").strip()) # R4
        schedule.semester = int(scheduleInfo[7].strip().removeprefix("S").strip()) # S7
        schedule.group = Group(scheduleInfo[8].strip().removeprefix("gr").strip()) # gr1

        split_filter = "------------------------------------------------"
        blocks: List[List[str]] = []
        # Divide file into blocks of lessons
        block:List[str] = []
        for line in data:
            if line == split_filter:
                blocks.append(block)
                block = []
            else:
                block.append(line)
        blocks.append(block)

        # Iterate over blocks
        # ZJ_01
        # Sztuczna Inteligencja [Lab]
        # d1, 10:30-12:00
        # 3/18
        # Aleksandra Konopka
        # U: 8 tygodni (ostatnie zajęcia 45 minut krócej)
        for block in blocks:
            lesson = Lesson()
            if "ZJ" not in block[0]:
                continue
            elif "end." in block:
                break

            # Parse text
            lesson.num = int(block[0].strip("ZJ_").strip())
            lesson.name = block[1].split("[")[0].strip()
            lesson.type = strToType(block[1].split("[")[1].split("]")[0].strip())
            # lesson.day = int(block[2].split(",")[0].strip().removeprefix("d").strip())
            lesson.day = DayOfWeek.fromInt(dayToDayNum(block[2].split(",")[0].strip().removeprefix("d").strip()))
            timeStartText = block[2].split(",")[1].split("-")[0].strip()
            lesson.startTime = datetime.strptime(timeStartText, "%H:%M").time()
            timeEndText = block[2].split(",")[1].split("-")[1].strip()
            lesson.endTime = datetime.strptime(timeEndText, "%H:%M").time()

            locationText = block[3].split(",")
            if len(locationText) >= 2:
                lesson.location.building = locationText[1].strip()
            else:
                lesson.location.building = "34"
            # lesson.location.floor = int(locationText[0].split("/")[0].strip() or None)
            # lesson.location.classroom = locationText[0].split("/")[1].strip() or locationText[0].strip()
            if len(locationText[0].split("/")) >= 2:
                lesson.location.floor = int(locationText[0].split("/")[0].strip())
                lesson.location.classroom = locationText[0].split("/")[1].strip()
            else:
                lesson.location.classroom = locationText[0].strip()

            lesson.location.building = block[3].split("/")[0].strip()
            lesson.lecturer.name = block[4].split(" ")[0].strip()
            lesson.lecturer.surname = block[4].split(" ")[1].strip()
            lesson.comment = block[5].removeprefix("U:").strip()

            # Add lesson to lessons list
            lessons.append(lesson)
        schedule.lessons = lessons
        return schedule

    @classmethod
    def get_timetables_from_file(cls, filename: str) -> List["Schedule"]:
        if filename.endswith(".txt"):
            with open(filename, "r") as f:
                return [cls.get_timetable_from_txt_data(f.read().splitlines())]
        elif filename.endswith(".xlsx"):
            with open(filename, "rb") as f:
                return cls.get_timetables_from_xlsx_data_openpyxl(BytesIO(f.read()))
        else:
            return []


    def to_map(self):
        return {
            "name": secureString(self.name())
        }

    def __str__(self):
        return f"Faculty: {self.faculty}\nField: {self.field}\nDegree: {self.degree}\nMode: {self.mode}\nYear: {self.year}\nSemester: {self.semester}\nGroup: {self.group}\nLessons: {self.lessons}"
