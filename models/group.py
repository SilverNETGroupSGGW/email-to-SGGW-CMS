from lib.string_safety import secureString


class Group:
    def __init__(self, name:str=""):
        self.name = name

    def to_map(self, scheduleID:str):
        return {
            "name": secureString(self.name),
            "scheduleId": secureString(scheduleID)
        }
