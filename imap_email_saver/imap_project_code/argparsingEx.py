from imap_fetch_mails import ImapMailClass
HOST = 'imap.gmail.com'
USERNAME = 'myusername'
PASSWORD = 'mysupersecretpassword'
ssl = True

obj = ImapMailClass(HOST, USERNAME, PASSWORD, ssl)
obj.fetch_message()

#server = obj.open_connection()

#print status
#print date
