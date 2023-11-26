from lib.string_safety import secureString


class Location:
    def __init__(self, name:str='', building:str='', floor: int | None = None):
        self.classroom = name
        self.building = building
        self.floor = floor

    def to_map(self):
        return {
            "name": secureString((f"{self.floor}/" or '') + self.classroom),
            "building": secureString(self.building)
        }

    def name(self):
        return (f"{self.floor}/" or '') + self.classroom

    def __str__(self):
        return f"{self.classroom}, {self.building}, {self.floor}"