from io import BytesIO
import lib.email_client as email_client
import lib.api_client as api_client
from models.emailMessage import EmailMessage
from models.schedule import Schedule

def processAttachmentsForNLastestEmail(i: int):
    # Get allowed senders from env
    import os
    allowedSenders = os.environ["ALLOWED_SENDERS"].split(",")
    email_prefix = os.environ.get("EMAIL_PREFIX") or ""

    # Add email prefix if set
    if email_prefix != "":
        email_prefix += "+"

    # Get latest email
    latestEmail:EmailMessage = email_client.getNLatestEmail(i) # 0 = latest email, 1 = second latest email, etc.

    # Check if email send to email with prefix
    if not latestEmail.recipient.startswith(email_prefix):
        print("Email not sent to email with prefix, skipping...")
        return

    # Check if sender is allowed
    if latestEmail.sender.split("<")[1].strip(">") not in allowedSenders:
        print("Sender " + latestEmail.sender + "not allowed, skipping...")
        return

    if len(latestEmail.attachments) == 0:
        print("No attachments, skipping...")
        return
    for attachment in latestEmail.attachments:
        if attachment.name.endswith(".xlsx"):
            print("Found Excel file, processing...")
            timetable = Schedule.get_timetables_from_xlsx_data_openpyxl(BytesIO(attachment.content))
            print(timetable)
        elif attachment.name.endswith(".txt"):
            print("Found text file, processing...")
            # Text is in UTF-8 with BOM
            timetable = Schedule.get_timetable_from_txt_data(attachment.content.decode("utf-8-sig").splitlines())
            print(timetable)
        else:
            print("Unknown file type, skipping...")

api_client.changePlanData(Schedule.get_timetables_from_file("plan.txt"))