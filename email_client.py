from pyclbr import Function
from classes import EmailMessage
from imapclient import IMAPClient
from typing import Callable

# Get username and password from environment variables
import os
username= os.environ.get('EMAIL_USERNAME')
password = os.environ.get('EMAIL_PASSWORD')
timeout = os.environ.get('TIMEOUT') or 2
imap_server = os.environ.get('IMAP_SERVER') or 'imap.gmail.com'

if username == None or password == None:
    raise Exception("USERNAME_OR_PASSWORD_NOT_SET")

if timeout == None:
    raise Exception("TIMEOUT_NOT_SET")

if imap_server == None:
    raise Exception("IMAP_SERVER_NOT_SET")

def getEmails():
    messages = client.search()
    emails = []
    for emailID in messages:
        raw_email = client.fetch(emailID, ['RFC822'])[emailID][b'RFC822']
        emailMessage = EmailMessage.from_raw_email(raw_email)
        emails.append(emailMessage)
    return emails

def getNLatestEmail(n):
    messages = client.search()
    emailID = messages[-n-1]
    raw_email = client.fetch(emailID, ['RFC822'])[emailID][b'RFC822']
    emailMessage = EmailMessage.from_raw_email(raw_email)
    return emailMessage

def listenForEmails(execOnNewEmail: Callable):
    # Start an IDLE (IMAP IDLE) command - allows the client to listen for changes
    client.idle()

    print("Listening for new emails...")
    while True:
        try:
            pass
        except Exception as e:
            print("Stopping due to exception: " + str(e))
            break
        responses = client.idle_check(timeout=timeout)
        if responses:
            for i, response in responses:
                execOnNewEmail(i)
    client.idle_done()

client = IMAPClient(imap_server)
client.login(username, password)
client.select_folder('INBOX')