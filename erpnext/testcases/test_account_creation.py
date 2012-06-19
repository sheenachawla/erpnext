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
import os
sys.path.append('lib/py')
sys.path.append('erpnext')

import webnotes


class TestAccountCreation(unittest.TestCase):
	def test(self):
		self.install_erpnext()
		
		webnotes.connect()
		self.check_default_records()
		self.setup_account()
		self.check_company_record()
		self.check_fiscal_year()
		self.check_chart_of_account()
		webnotes.conn.close()
		
		
	def install_erpnext(self):
		if raw_input("Do you want to install erpnext (Y/N)?") in ('Y', 'y'):
			os.system('python install_erpnext.py')
		
	def check_default_records(self):
		print "Checking account creation by creation 'INR' currency......"
		currency = webnotes.conn.sql("select name from `tabCurrency` where name = 'INR'")[0][0]
		self.assertTrue('INR', currency)
		print "currency: " + currency + ' found'		
				
	def setup_account(self):
		if raw_input("Do you want to run company setup (Y/N)?") in ('Y', 'y'):
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
		
		
	def check_company_record(self):
		print "Checking company......"
		comp, abbr = webnotes.conn.sql("select name, abbr from `tabCompany` where docstatus != 2")[0]
		self.assertTrue(comp, 'Test Company')
		self.assertTrue(abbr, 'TC')
		print "Company %s found" % comp
		
	def check_fiscal_year(self):
		print "Checking fiscal year and period......"
		fy = webnotes.conn.sql("select name from `tabFiscal Year` where docstatus != 2")[0][0]
		self.assertTrue(fy)
		print "Fiscal Year %s found" % fy
		
		period_count = webnotes.conn.sql("select count(name) from `tabPeriod` where fiscal_year = %s \
			and docstatus != 2", fy)[0][0]
		self.assertTrue(period_count, 13)
		print "%s Period found" % period_count
		
	def check_chart_of_account(self):
		print "Checking chart of accounts......"
		roots = [d[0] for d in webnotes.conn.sql("select account_name from `tabAccount` \
			where ifnull(parent_account, '') = '' and docstatus < 2")]
		self.assertEqual(roots, ['Application of Funds (Assets)', 'Expenses', 'Income', 'Source of Funds (Liabilities)'])
		print str(roots) + 'found'
		
		
	def check_cost_center(self):
		pass
		
	def check_account_balance(self):
		pass
		
	def check_global_defaults(self):
		pass
		
		
		
if __name__ == '__main__':
	unittest.main()