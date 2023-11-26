from lib.string_safety import secureString


class Lecturer:
    def __init__(self, name:str='', surname:str = '', email:str='', degree:str=''):
        self.name = name
        self.surname = surname
        self.email = email
        self.degree = degree

    def to_map(self):
        return {
            "firstName": secureString(self.name),
            "surname": secureString(self.surname),
            "academicDegree": secureString(self.degree),
            "email": secureString(self.email),
        }

    def __str__(self):
        return f"{self.name}, {self.email}"
