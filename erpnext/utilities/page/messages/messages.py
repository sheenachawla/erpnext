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
	webnotes.form['limit_start'] = int(webnotes.form['limit_start'])
	webnotes.form['limit_page_length'] = int(webnotes.form['limit_page_length'])
	webnotes.form['user'] = webnotes.session['user']

	if webnotes.form['contact'] == webnotes.session['user']:
		# set all messages as read
		webnotes.conn.sql("""UPDATE `tabComment`
		set docstatus = 1 where parenttype in ('My Company', 'Message')
		and parent = %s
		""", webnotes.user.name)
				
		# return messages
		return webnotes.conn.sql("""select * from `tabComment` 
		where (owner=%(contact)s or parent=%(user)s)
		and parenttype in ('My Company', 'Message')
		order by creation desc
		limit %(limit_start)s, %(limit_page_length)s""", webnotes.form, as_dict=1)		
	else:
		return webnotes.conn.sql("""select * from `tabComment` 
		where (owner=%(contact)s and parent=%(user)s)
		or (owner=%(user)s and parent=%(contact)s)
		and parenttype in ('My Company', 'Message')
		order by creation desc
		limit %(limit_start)s, %(limit_page_length)s""", webnotes.form, as_dict=1)
		

@webnotes.whitelist()
def get_active_users(arg=None):
	return webnotes.conn.sql("""select name from tabProfile 
		where ifnull(enabled,0)=1 and
		docstatus < 2 and 
		name not in ('Administrator', 'Guest') 
		order by first_name""", as_dict=1)

@webnotes.whitelist()
def post(arg=None):
	import webnotes
	"""post message"""
	if arg:
		import json
		arg = json.loads(arg)
	else:
		arg = {}
		arg.update(webnotes.form)
	from webnotes.model.doc import Document
	d = Document('Comment')
	d.comment = arg['txt']
	d.parent = arg['contact']
	d.parenttype = 'Message'
	d.save()

	import webnotes.utils
	if webnotes.utils.cint(arg.get('notify')):
		notify(arg)
	
@webnotes.whitelist()
def delete(arg=None):
	webnotes.conn.sql("""delete from `tabComment` where name=%s""", 
		webnotes.form['name']);

def notify(arg=None):
	from webnotes.utils import cstr
	fn = webnotes.conn.sql('select first_name, last_name from tabProfile where name=%s', webnotes.user.name)[0]
	if fn[0] or f[1]:
		fn = cstr(fn[0]) + (fn[0] and ' ' or '') + cstr(fn[1])
	else:
		fn = webnotes.user.name

	message = '''A new comment has been posted on your page by %s:
	
	<b>Comment:</b> %s
	
	To answer, please login to your erpnext account!

	<a href='https://signin.erpnext.com'>https://signin.erpnext.com</a>
	''' % (fn, arg['txt'])
	
	from webnotes.model.code import get_obj
	note = get_obj('Notification Control')
	email_msg = note.prepare_message({
		'type': 'New Comment',
		'message': message
	})

	sender = webnotes.user.name!='Administrator' and webnotes.user.name or 'support+admin_post@erpnext.com'
	
	from webnotes.utils.email_lib import sendmail
	sendmail([arg['contact']], sender, email_msg, fn + ' has posted a new comment')	
