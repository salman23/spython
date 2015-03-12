# -*- coding: utf-8 -*-
__author__ = 'salman wahed'

SMTPSERVER = 'smtp.sendgrid.net'

# credential for login
USERNAME = "***"
PASSWORD = "***"

from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText


def send_mail(from_addr, to_addr, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    connection = SMTP(SMTPSERVER)
    connection.set_debuglevel(False)
    try:
        connection.login(USERNAME, PASSWORD)
        connection.sendmail(from_addr, to_addr, msg.as_string())
        print "Mail Sent!"
    except Exception as e:
        print e.message
    finally:
        connection.close()

from_addr = 'python@smtp.mail'
to_addr = ['email@example.com']
subject = "My awesome mail"
body = """
Hello World,
    This is a smtp mail sending from python.
regards,
salman wahed.
"""
send_mail(from_addr, to_addr, subject, body)