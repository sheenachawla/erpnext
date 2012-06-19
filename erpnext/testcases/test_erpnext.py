
import unittest, sys
import os
sys.path.append('lib/py')
sys.path.append('erpnext')

import webnotes

def install_erpnext(rootpwd, dbname, pwd):
	os.system('python install_erpnext.py %s %s %s' % (rootpwd, dbname, pwd))
	#setup
	webnotes.connect()
	setup_account()
	webnotes.conn.close()
	
			
def setup_account():
	args = {
		'first_name': 'Nabin',
		'last_name': 'Hait',
		'company_name': 'Test Company',
		'company_abbr': 'TC',
		'fy_start': '1st Apr',
		'currency': 'INR',
		'industry': 'Information Technology',
		'country': 'India',
		'timezone': 'Asia/Calcutta'
	}
	import json
	from webnotes.model.code import get_obj
	get_obj('Setup Control').setup_account(json.dumps(args))

#---------------------------------------------------------------

from test_account_setup import *

def setup_options():
	from optparse import OptionParser
	parser = OptionParser()
	
	parser.add_option('-i', '--install', dest='install', nargs=3, metavar = "rootpassword dbname pwd",
						help="install fresh db and setup company")
		
	return parser.parse_args()

def run():
	(options, args) = setup_options()
	
	if options.install:
		install_erpnext(options.install[0], options.install[1], options.install[2])
		
	unittest.main()

if __name__ == '__main__':
	run()