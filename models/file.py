class File:
    def __init__(self, name: str="", content: bytes=b""):
        self.name = name
        self.content = content

    def save(self, folder: str = "./", name: str|None=None):
        import os
        if not os.path.isdir(folder):
            os.mkdir(folder)

        with open(os.path.join(folder, name or self.name), "wb") as f:
            f.write(self.content)

    def __str__(self):
        return f"Name: {self.name}\nContent: {self.content}"