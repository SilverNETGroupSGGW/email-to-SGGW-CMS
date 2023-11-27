from io import BytesIO
import lib.email_client as email_client
import lib.api_client as api_client
from models.emailMessage import EmailMessage
from models.schedule import Schedule
from lib.logger import logger


def processAttachmentsForLastestValidEmail():
    # Get allowed senders from env
    import os
    allowedSenders = (os.environ.get("ALLOWED_SENDERS") or "").split(",")
    email_prefix = os.environ.get("EMAIL_PREFIX") or ""

    # Add email prefix if set
    if email_prefix != "":
        email_prefix += "+"

    i:int = -1
    latestEmail = EmailMessage()
    while i < 10:
        i += 1
        # Get latest email
        latestEmail = email_client.getNLatestEmail(i) # 0 = latest email, 1 = second latest email, etc.
        if latestEmail == None:
            logger.info("No emails found, skipping...")
            return
        # Check if email send to email with prefix
        if not latestEmail.recipient.startswith(email_prefix):
            print("Email not sent to email with prefix, skipping...")
            continue

        # Check if sender is allowed
        if latestEmail.sender.split("<")[1].strip(">") not in allowedSenders:
            logger.info("Sender " + latestEmail.sender + " is not allowed, skipping...")
            continue

        if len(latestEmail.attachments) == 0:
            logger.info("No attachments, skipping...")
            continue
        break

    for attachment in latestEmail.attachments:
        if attachment.name.endswith(".xlsx"):
            logger.info("Found Excel file, processing...")
            timetable = Schedule.get_timetables_from_xlsx_data_openpyxl(BytesIO(attachment.content))
            logger.info("Sending data to API...")
            api_client.changePlanData(timetable)
            logger.info("Done")
        elif attachment.name.endswith(".txt"):
            logger.info("Found text file, processing...")
            # Text is in UTF-8 with BOM
            timetable = Schedule.get_timetable_from_txt_data(attachment.content.decode("utf-8-sig").splitlines())
            logger.info("Sending data to API...")
            api_client.changePlanData([timetable])
            logger.info("Done")
        else:
            logger.warning("Unknown file type, skipping...")

processAttachmentsForLastestValidEmail()
email_client.listenForEmails(processAttachmentsForLastestValidEmail)