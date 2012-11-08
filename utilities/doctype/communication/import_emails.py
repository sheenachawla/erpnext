# ERPNext - web based ERP (http://erpnext.com)
# Copyright (C) 2012 Web Notes Technologies Pvt Ltd
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import webnotes
from webnotes.utils import cstr, cint
from webnotes.utils.email_lib.receive import POP3Mailbox

class CommunicationMailbox(POP3Mailbox):
	def __init__(self, profile):
		self.profile = profile
		self.with_attachments = True
		self.import_all = False

	def set_connection_params(self):
		if not self.profile:
			webnotes.msgprint("User not set", raise_exception=1)

		self.profile_obj = webnotes.get_doc("Profile", self.profile)
		
		if not self.profile_obj.sync_emails: 
			return
		
		self.settings = webnotes.DictObj()
		self.settings.use_ssl = self.profile_obj.mail_use_ssl
		self.settings.host = self.profile_obj.mail_host
		self.settings.username = self.profile_obj.mail_login
		self.settings.password = self.profile_obj.mail_password

	def process_message(self, mail):
		"""create new communication if exists in contact / profile"""
		from email.utils import parseaddr, formataddr
		real_name, email_id = parseaddr(mail.mail["From"])

		self.communication = webnotes.get_doc({
			"doctype":"Communication",
			"__islocal": 1,
			"communication_medium": "Email",
			"status": "Open"
		})
		
		if self.do_import(email_id):
			content, content_type = mail.get_content_and_type()
			self.communication.fields.update({
				"naming_series": self.get_naming_series(),
				"subject": self.scrub_subject(mail.mail["Subject"]),
				"content": content,
				"thread": self.get_thread()
				"from_email": email_id,
				"from_real_name": real_name
			})
						
			webnotes.model_wrapper([self.communication]).save()

			if self.with_attachments:
				# extract attachments
				self.save_attachments(self.communication, mail.attachments)
			
	def do_import(self, email_id):
		contact = webnotes.conn.sql("""select name from tabContact 
			where email_id=%s""", email_id)
		if contact:
			self.communication.contact = contact[0][0]
			return True

		lead = webnotes.conn.sql("""select name from tabLead 
			where email_id=%s""", email_id)
		if lead:
			self.communication.lead = lead[0][0]
			return True

		user = webnotes.conn.sql("""select name from tabProfile 
			where email=%s""", email_id)
		if user:
			self.communication.user = user[0][0]
			return True

		if self.import_all: 
			return True

		return False
	
	def get_naming_series(self):
		from webnotes.model.doctype import get_property
		opts = get_property('Support Ticket', 'options', 'naming_series')
		return opts and opts.split("\n")[0] or "COMM"
	
	def scrub_subject(self, subject):		
		if subject.startswith("Re:"):
			subject = subject[3:].strip()

		if subject.startswith("Fwd:"):
			subject = subject[4:].strip()
			
		return subject
			
	def get_thread(self):
		if not self.communication.subject:
			return None
		
		thread = webnotes.conn.sql("""select name from tabCommunication 
			where subject=%s limit 1""", self.communication.subject)
		if thread:
			thread = thread[0][0]
			
			# set status as status Open
			webnotes.conn.sql("""update tabCommunication set status='Open'
				where name=%s""", thread)
			return thread
		else:
			return None
		
		
class SupportMailbox(CommunicationMailbox):
	def __init__(self):
		self.category = "Support"
		self.import_all = True
		
	def set_connection_params(self):
		self.email_settings = webnotes.get_doc("Email Settings")
		if not self.email_settings.sync_support_mails: 
			return

		self.settings = webnotes.DictObj()
		self.settings.use_ssl = self.email_settings.support_use_ssl
		self.settings.host = self.email_settings.support_host
		self.settings.username = self.email_settings.support_username
		self.settings.password = self.email_settings.support_password	
		
	def autoreply(self, d):
		"""Send auto reply to emails"""
		from webnotes.utils import cstr
		signature = self.email_settings.support_signature or ''
		response = self.email_settings.support_autoreply or ("""
A new Ticket has been raised for your query. If you have any additional information, 
please reply back to this mail. 

We will get back to you as soon as possible.

[This is an automatic response]

		""" + cstr(signature))

		from webnotes.utils.email_lib import sendmail
		
		sendmail(\
			recipients = [cstr(self.mail["From"])],
			sender = cstr(self.email_settings.support_email),
			subject = 'Re: ' + cstr(d.subject),
			msg = cstr(response))
		
		self.auto_close_tickets()
		
	def auto_close_tickets(self):
		webnotes.conn.sql("""update `tabCommunication` set status = 'Closed' 
			where status = 'Waiting for Customer' 
			and date_sub(curdate(),interval 15 Day) > modified""")

def import_emails():
	# support
	if cint(webnotes.conn.get_value('Email Settings', None, 'sync_support_mails')):
		SupportMailbox().get_messages()
		
	for profile in webnotes.conn.sql("""select name from tabProfile 
		where ifnull(sync_emails, 0)=1"""):
		CommunicationMailbox(profile[0]).get_messages()