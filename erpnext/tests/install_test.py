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

def load_data(session):
	"""install freshdb and run setup"""
	
	import conf, getpass
	from webnotes.install_lib.install import Installer
	
	root_pwd = getpass.getpass("MySQL Root user's Password: ")
	
	inst = Installer('root', root_pwd)
	inst.import_from_db(conf.test_db_name, verbose = 1)

	args = {
		'first_name': 'John',
		'last_name': 'Doe',
		'company_name': 'East Wind Corporation',
		'company_abbr': 'EW',
		'fy_start': '1st Apr',
		'currency': 'INR',
		'industry': 'Information Technology',
		'country': 'India',
		'timezone': 'Asia/Calcutta'
	}
	import json
	session.controller("Setup Control", "Setup Control").setup_account(json.dumps(args))
