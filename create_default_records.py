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

def set_home_page():
	"""Set default home page"""
	webnotes.conn.set_value('Control Panel', 'Control Panel', 'home_page', 'desktop')
	
def set_cp_defaults():
	""" save global defaults and features setup"""
	from webnotes.model.code import get_obj
	get_obj('Global Defaults').on_update()
	get_obj('Features Setup').validate()

	
def set_all_roles_to_admin():
	"""Set all roles to administrator profile"""
	from webnotes.model.doc import Document
	from setup.doctype.setup_control import setup_control
	prof = Document('Profile', 'Administrator')
	setup_control.add_roles(prof)
	

	
