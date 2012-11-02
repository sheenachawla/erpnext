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

@webnotes.whitelist()
def get_list(arg=None):
	"""get list of messages"""
	webnotes.form_dict['limit_start'] = int(webnotes.form_dict['limit_start'])
	webnotes.form_dict['limit_page_length'] = int(webnotes.form_dict['limit_page_length'])
	webnotes.form_dict['user'] = webnotes.session['user']

	# set all messages as read
	webnotes.conn.sql("""UPDATE `tabComment`
	set docstatus = 1 where comment_doctype in ('My Company', 'Message')
	and comment_docname = %s
	""", webnotes.user.name)

	# all messages
	if webnotes.form_dict['contact'] == webnotes.session['user']:
		return webnotes.conn.sql("""select * from `tabComment` 
		where (owner=%(contact)s 
			or comment_docname=%(user)s 
			or (owner=comment_docname and ifnull(parenttype, "")!="Assignment"))
		and comment_doctype ='Message'
		order by creation desc
		limit %(limit_start)s, %(limit_page_length)s""", webnotes.form_dict, as_dict=1)		
	else:
		return webnotes.conn.sql("""select * from `tabComment` 
		where (owner=%(contact)s and comment_docname=%(user)s)
		or (owner=%(user)s and comment_docname=%(contact)s)
		or (owner=%(contact)s and comment_docname=%(contact)s)
		and comment_doctype ='Message'
		order by creation desc
		limit %(limit_start)s, %(limit_page_length)s""", webnotes.form_dict, as_dict=1)
		

@webnotes.whitelist()
def get_active_users(arg=None):
	return webnotes.conn.sql("""select name,
		(select count(*) from tabSessions where user=tabProfile.name
			and timediff(now(), lastupdate) < time("01:00:00")) as has_session
	 	from tabProfile 
		where ifnull(enabled,0)=1 and
		docstatus < 2 and 
		name not in ('Administrator', 'Guest') 
		order by first_name""", as_dict=1)

@webnotes.whitelist()
def post(txt=None, contact=None, notify_by_email=False, parenttype=None):
	import webnotes
	"""post message"""
	from webnotes.model.doc import Document
	
	if not txt or not contact:
		webnotes.msgprint("Message and Recipient must be given.", raise_exception=1)
	
	d = Document('Comment')
	d.comment = txt
	d.comment_docname = contact
	d.comment_doctype = 'Message'
	if parenttype:
		d.parenttype = parenttype
	d.save()

	import webnotes.utils
	if notify_by_email:
		notify(contact, txt)
	
@webnotes.whitelist()
def delete(arg=None):
	webnotes.conn.sql("""delete from `tabComment` where name=%s""", 
		webnotes.form_dict['name']);

def notify(contact, txt):
	from webnotes.utils import cstr
	fn = webnotes.conn.sql("""select first_name, last_name 
		from tabProfile where name=%s""", webnotes.user.name)[0]
	if fn[0] or f[1]:
		fn = cstr(fn[0]) + (fn[0] and ' ' or '') + cstr(fn[1])
	else:
		fn = webnotes.user.name

	message = '''A new comment has been posted on your page by %s:
	
	<b>Comment:</b> %s
	
	To answer, please login to your erpnext account!
	''' % (fn, txt)
	
	from webnotes.model.controller import get_obj
	note = get_obj('Notification Control')
	email_msg = note.prepare_message({
		'type': 'New Comment',
		'message': message
	})

	sender = webnotes.user.name!='Administrator' and webnotes.user.name or 'support+admin_post@erpnext.com'
	
	from webnotes.utils.email_lib import sendmail
	sendmail(contact, sender, email_msg, fn + ' has posted a new comment')	
