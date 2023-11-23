from classes import Lesson, Schedule
import email_client

def processAttachmentsForNLastestEmail(i):
    # Get allowed senders from env
    import os
    allowedSenders = os.environ['ALLOWED_SENDERS'].split(',')
    email_prefix = os.environ.get('EMAIL_PREFIX') or ''

    # Add email prefix if set
    if email_prefix != '':
        email_prefix += "+"

    # Get latest email
    latestEmail = email_client.getNLatestEmail(i) # 0 = latest email, 1 = second latest email, etc.

    # Check if email send to email with prefix
    if not latestEmail.recipient.startswith(email_prefix):
        print("Email not sent to email with prefix, skipping...")
        return

    # Check if sender is allowed
    if latestEmail.sender not in allowedSenders:
        print("Sender " + latestEmail.sender + "not allowed, skipping...")
        return

    if len(latestEmail.attachments) == 0:
        print("No attachments, skipping...")
        return
    for attachment in latestEmail.attachments:
        if attachment.name.endswith('.xlsx'):
            print("Found Excel file, processing...")
            timetable = Schedule.getTimetableFromTXTData(attachment.content)
            print(timetable)
        elif attachment.name.endswith('.txt'):
            print("Found text file, processing...")
            timetable = Schedule.getTimetablesFromXLSXData(attachment.content)
            print(timetable)
        else:
            print("Unknown file type, skipping...")

schedules = Schedule.getTimetablesFromFile('plan.xlsx')
for schedule in schedules:
    print(schedule)
    for lesson in schedule.lessons:
        print(lesson)