import unittest, sys
import os
sys.path.append('lib/py')
sys.path.append('erpnext')

import webnotes


#---------------------------------------------------------------
# Import all test files here - implement os.walk later

from test_account_setup import *
from test_stock_entry import *
#from test_serialized_inventory import *
#from webnotes.utils.nestedset import *
from test_masters import *
from test_sales_order import *
from test_delivery_note import *


def install_erpnext(rootpwd, dbname, pwd):
	os.system('python install_erpnext.py %s %s %s' % (rootpwd, dbname, pwd))
	#setup
	webnotes.connect()
	print "Setting up account..."
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


def setup_options():
	from optparse import OptionParser
	parser = OptionParser()
	
	parser.add_option('-i', '--install', dest='install', nargs=3, metavar = "rootpassword dbname pwd",
						help="install fresh db and setup company")
		
	return parser.parse_args()


def run():
	options, args = setup_options()
	
	if options.install:
		install_erpnext(options.install[0], options.install[1], options.install[2])
	
	# delete all command line arguments before run testcases
	del sys.argv[1:]
	
	webnotes.connect()
	unittest.main()
	webnotes.conn.close()

if __name__ == '__main__':
	run()