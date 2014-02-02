from __future__ import unicode_literals
import imaplib
import re
from email import email
from email.parser import HeaderParser
from StringIO import StringIO
import argparse
import os

class ImapMailClass(object):
	"""docstring for ImapMailClass"""
	def __init__(self, host, username, password, ssl):
		self.host = host
		self.username = username
		self.password = password
		self.ssl = ssl
	
	def _run_modes(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('--status', '-status', help= 'status of the mails')
		parser.add_argument('--fromdate', '-fromdate', help= 'write -fromdate/--fromdate followed by date in dd-Mmm-yyyy pattern')
		parser.add_argument('--mailto', '-mailto', help= 'write -to/--to followed by email address in email@example.com pattern')
		parser.add_argument('--mailfrom', '-mailfrom', help= 'write -from/--from followed email address in email@example.com pattern')
		args =  parser.parse_args()
		statuses = ['UNREAD', 'unread', 'UNSEEN', 'Unread']
		
		if args.status in statuses:
			mail_flag = 'UNSEEN'
		else:
			mail_flag = 'ALL'
		if args.fromdate:
			date = args.fromdate
		else:
			date = None
		
		if args.mailto:
			mailto = 'TO '+'"'+args.mailto+'"'
			#print mailto
		else: mailto = None
		
		if args.mailfrom:
			mailfrom = 'FROM '+'"'+args.mailfrom+'"'
			#print mailfrom
		else: mailfrom = None
		
		return mail_flag, date, mailto, mailfrom

	def _parse_list_response(self, line):
		list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
		flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
		mailbox_name = mailbox_name.strip('"')
		return (flags, delimiter, mailbox_name)

	def _get_mailbox_name(self):
		mailboxes = []
		server = self._open_connection()
		typ, data = server.list()
		for line in data:
			flags, delimiter, mailbox_name = self._parse_list_response(line)
			mailboxes.append(mailbox_name)
		return mailboxes


	def _open_connection(self):
		server = imaplib.IMAP4_SSL(self.host) #connect to the server
		server.login(self.username, self.password) # login to the host name
		return server


	def _get_msg_id(self, mailbox):
		server = self._open_connection()
		mail_flag, date, mailto, mailfrom = self._run_modes()
		status, data = server.select(mailbox, readonly=True)
		
		if date:
			typ, msg_ids = server.search(None, 'SINCE', date)
		
		else:
			typ, msg_ids = server.search(None, mail_flag)

		if mailto:
			typ, msg_ids = server.search(None, (mailto))

		if mailfrom:
			typ, msg_ids = server.search(None, (mailfrom))	
		
		id_list =  msg_ids[0].split()
		#print id_list
		return id_list

	def _parse_attachment(self,message_part):
		content_disposition = message_part.get("Content-Disposition", None)
		if content_disposition:
			dispositions = content_disposition.strip().split(";")
			if bool(content_disposition and dispositions[0].lower() == "attachment"):

				file_data = message_part.get_payload(decode=True)
				attachment = StringIO(file_data)
				attachment.content_type = message_part.get_content_type()
				attachment.size = len(file_data)
				attachment.name = None
				
				for param in dispositions[1:]:
					name,value = param.split("=")
					attachment.name = value

				return attachment, file_data
		return None

	def fetch_message(self):
		attachments = []
		body = None
		mailboxes = ['INBOX', '"[Gmail]/Sent Mail"']
		
		date_pat = re.compile(r'\d*\s\D*\s\d*')
		
		for mailbox in mailboxes:
			server = self._open_connection()
			server.select(mailbox, readonly = True)
			msg_ids = self._get_msg_id(mailbox)

			for msg_id in msg_ids:
				typ, data = server.fetch(msg_id, '(RFC822)')
				header_data = data[0][1]
				parser = HeaderParser()
				header_msg = parser.parsestr(header_data)
				date = re.findall(date_pat, header_msg['Date'])[0]
				subject  = header_msg['Subject']

				msgobj = email.message_from_string(data[0][1])

				for part in msgobj.walk():
					try:
						attachment, file_data = self._parse_attachment(part)
					except TypeError:
						attachment = None
					
					if attachment:
						attachments.append(attachment)
						self.write_file_data(attachment,file_data, mailbox, date, subject)

					elif part.get_content_type() == "text/plain":
						try:
							if body is None:
								body = ""
							body += unicode(
								part.get_payload(decode=True),
								part.get_content_charset(),
								'replace'
								).encode('utf8','replace')

						except UnicodeDecodeError:
							continue
					
				#mail = {'body': body, 'subject' : header_msg['Subject'], 'date': date, 'from' : header_msg['From'], 'to' : header_msg['To'], 'attachments': at_name}
				mail = ('to:' +header_msg['To']+'\n' +'from:' + header_msg['From']+ '\n' + 'subject:'+ subject + '\n' +'body:'+body)
				self.write_file_data(None, mail, mailbox, date, subject)
				attachments = []
				body = None


	def write_file_data(self, attachment, file_data, mailbox, date, subject):
		if attachment:
			filename = attachment.name
		else:
			filename = subject+ '_body.txt'
		
		filedir = date + '_' +subject

		inboxdir = "/directory/to/save/imapmails/inbox/" 
		sentdir = "/directory/to/save/imapmails/sent/"
		if filename is not None:
			if mailbox =='INBOX':
				if os.path.exists(inboxdir):
					save_file_dir = inboxdir+filedir +'/'
					
					if os.path.exists(save_file_dir):
						if self._isThere(save_file_dir, filename):
							print '(%s)file exists in %s' %(filename,save_file_dir)
							pass
						else:
							self.write_it(save_file_dir, filename, file_data)
					else:
						os.mkdir(save_file_dir)
						self.write_it(save_file_dir, filename, file_data)	
				else:
					os.mkdir(inboxdir)
					save_file_dir = inboxdir + filedir +'/'
					os.mkdir(save_file_dir)
					self.write_it(save_file_dir, filename, file_data)
			
			if mailbox =='"[Gmail]/Sent Mail"':
				if os.path.exists(sentdir):
					save_file_dir = sentdir + filedir +'/'

					if os.path.exists(save_file_dir):
						if self._isThere(save_file_dir, filename):
							print '(%s)file exists in %s' %(filename,save_file_dir)
							pass
						else:
							self.write_it(save_file_dir, filename, file_data)
					else:
						os.mkdir(save_file_dir)
						self.write_it(save_file_dir, filename, file_data)
				else:
					os.mkdir(sentdir)
					save_file_dir = sentdir + filedir +'/'
					os.mkdir(save_file_dir)
					self.write_it(save_file_dir, filename, file_data)
				

	def write_it(self,directory, filename, file):
		filedir = directory + filename
		fp = open(filedir, 'wb')
		fp.write(file)
		fp.close

	def _isThere(self,directory,filename):
		for root, dirs, files in os.walk(directory):
			if filename in files:
				return os.path.join(root, filename)