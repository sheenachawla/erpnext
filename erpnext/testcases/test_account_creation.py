"""
To-do
--------
1. account creation and checking any of the records
2. call company creation and check if it is created
3. check fiscal year and period
4. check global defaults properly set in control panel
5. check chart of accounts and cost center created


"""

import unittest, sys
sys.path.append('lib/py')

import webnotes


class TestAccountCreation(unittest.TestCase):
	def test_install_erpnext(self):
		import os
		os.system('python install_erpnext.py')
		webnotes.session = {'user': 'Administrator'}
		webnotes.connect()
		
		# checking account creation by creation "INR" currency
		currency = webnotes.conn.sql("select name from `tabCurrency` where name = 'INR'")[0][0]
		print "currency: " + currency
		self.assertTrue('INR', currency)
		
	def setup_account(self):
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
		
	def test_company_record(self):
		webnotes.session = {'user': 'Administrator'}
		webnotes.connect()
		
		self.setup_account()
		comp, abbr = sql("select name, company_abbr from `tabCompany`")[0]
		self.assertTrue(comp, 'Test Company')
		self.assertTrue(abbr, 'TC')
		
		
		
if __name__ == '__main__':
	unittest.main()