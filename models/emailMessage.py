from models.file import File
from typing import List
from email.message import Message

class EmailMessage:
    def __init__(self, subject:str="", sender:str="", recipient:str="", date:str="", body:str="", attachments:List[File]=[]):
        if len(attachments) == 0:
            attachments = []
        self.subject = subject
        self.sender = sender
        self.recipient = recipient
        self.date = date
        self.body = body
        self.attachments: List[File] = attachments

    @classmethod
    def from_raw_email(cls, raw_email: bytes):
        import email
        def extract_body(parsed_email: Message):
            body = ""
            if parsed_email.is_multipart():
                for part in parsed_email.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get("Content-Disposition"))

                    # skip any text/plain (txt) attachments
                    if ctype == "text/plain" and "attachment" not in cdispo:
                        body = part.get_payload(decode=True)
                        break
            # not multipart - i.e. plain text, no attachments, keeping fingers crossed
            else:
                body = parsed_email.get_payload(decode=True)
            return body


        def extract_attachments(parsed_email: Message):
            attachments:List[File] = []
            for part in parsed_email.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue

                filename = part.get_filename()
                if bool(filename):
                    attachments.append(File(filename, part.get_payload(decode=True)))
            return attachments

        parsed_email = email.message_from_bytes(raw_email)
        subject = parsed_email["Subject"]
        sender = parsed_email["From"]
        recipient = parsed_email["To"]
        date = parsed_email["Date"]
        body = extract_body(parsed_email)
        attachments = extract_attachments(parsed_email)

        return cls(subject, sender, recipient, date, body, attachments)


    def save_attachments(self, folder: str = "./Attachments"):
        import os
        if not os.path.isdir(folder):
            os.mkdir(folder)

        for attachment in self.attachments:
            attachment.save(folder, attachment.name)

    def __str__(self):
        return f"Subject: {self.subject}\nFrom: {self.sender}\nTo: {self.recipient}\nDate: {self.date}\nBody: {self.body}\nAttachments: {self.attachments}"
