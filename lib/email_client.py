from imapclient import IMAPClient
from imapclient.response_types import SearchIds
from typing import Callable, List
from models.emailMessage import EmailMessage
from lib.logger import logger

# Get username and password from environment variables
import os
username= os.environ.get("EMAIL_USERNAME")
password = os.environ.get("EMAIL_PASSWORD")
timeout = os.environ.get("TIMEOUT") or 20
imap_server = os.environ.get("IMAP_SERVER") or "imap.gmail.com"

if username == None or password == None:
    raise Exception("EMAIL_USERNAME_OR_PASSWORD_NOT_SET")

def getEmails():
    messages:SearchIds = fetcher.search()
    emails:List[EmailMessage] = []
    for emailID in messages:
        raw_email:bytes = fetcher.fetch(emailID, ["RFC822"])[emailID][b"RFC822"]
        emailMessage = EmailMessage.from_raw_email(raw_email)
        emails.append(emailMessage)
    return emails

def getNLatestEmail(n: int):
    logger.info("Getting latest " + str(n+1) + ". email...")
    messages = fetcher.search()
    if len(messages) == 0:
        logger.info("No new emails, skipping...")
        return None
    # Check if there any mail doesn't have the flag \
    emailID = messages[-n-1]
    raw_email = fetcher.fetch(emailID, ["RFC822"])[emailID][b"RFC822"]
    fetcher.set_flags(emailID, [b"\\Seen"])
    emailMessage = EmailMessage.from_raw_email(raw_email)
    return emailMessage

def listenForEmails(execOnNewEmail: Callable[[], None]):
    # Start an IDLE (IMAP IDLE) command - allows the client to listen for changes
    client.idle()

    logger.info("Listening for new emails...")
    while True:
        try:
            pass
        except Exception as e:
            print("Stopping due to exception: " + str(e))
            break
        responses = client.idle_check(timeout=timeout)
        if len(responses) > 0:
            logger.info("Got event")
            i: int=0
            while i < len(responses):
                execOnNewEmail()
                i += 1
    client.idle_done()

client = IMAPClient(imap_server)
fetcher = IMAPClient(imap_server)
client.login(username, password)
fetcher.login(username, password)
client.select_folder("INBOX")
fetcher.select_folder("INBOX")