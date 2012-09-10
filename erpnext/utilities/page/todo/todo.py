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

import webnotes
from webnotes.model.doc import Document

@webnotes.whitelist()
def get(arg=None):
	"""get todo list"""
	return webnotes.conn.sql("""select name, owner, description, date,
		priority, checked, parenttype, parent, assigned_by
		from `tabToDo` where (owner=%s or assigned_by=%s)
		order by field(priority, 'High', 'Medium', 'Low') asc, date asc""",
		(webnotes.session['user'], webnotes.session['user']), as_dict=1)
