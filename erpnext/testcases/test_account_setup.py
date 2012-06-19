"""
To-do
--------
check global defaults properly set in control panel
check chart of accounts and cost center created


"""

import unittest, sys
import os
sys.path.append('lib/py')
sys.path.append('erpnext')

import webnotes
from webnotes.utils import cstr, cint, flt, get_defaults, getdate, add_days, get_first_day



class TestAccountSetup(unittest.TestCase):
	def setUp(self):
		webnotes.connect()
		webnotes.conn.begin()
		print '_'*40
		
	
	def test_default_records(self):
		print "Checking currency"
		currency = webnotes.conn.sql("select name from `tabCurrency` where name = 'INR'")[0][0]
		self.assertTrue('INR', currency)
		print "Currency: " + currency + ' found'
		
		
	def test_company_record(self):
		print "Checking company"
		comp, abbr = webnotes.conn.sql("select name, abbr from `tabCompany` where docstatus != 2")[0]
		self.assertTrue(comp, 'Test Company')
		self.assertTrue(abbr, 'TC')
		print "Company: %s found" % comp
		
	def test_fiscal_year(self):
		print "Checking fiscal year and period"
		fy = webnotes.conn.sql("select name, year_start_date from \
			`tabFiscal Year` where docstatus != 2")[0]
		self.assertTrue(fy[0])
		print "Fiscal Year: %s found" % fy[0]
		
		period_count = webnotes.conn.sql("select count(name) from `tabPeriod` \
			where fiscal_year = %s and docstatus != 2", fy[0])[0][0]
		self.assertTrue(period_count, 13)
		print "%s Period found" % period_count
		
		#global def
		self.assertEqual(fy[0], get_defaults('fiscal_year'))
		self.assertEqual(getdate(fy[1]).strftime('%Y-%m-%d'), get_defaults('year_start_date'))
		
		yed = add_days(get_first_day(getdate(fy[1]),0,12), -1)
		self.assertEqual(yed, get_defaults('year_end_date'))
		
		
	def test_chart_of_account(self):
		print "Checking chart of accounts"
		
		#check root accounts
		roots = webnotes.conn.sql("select account_name, lft, rgt from `tabAccount` \
			where ifnull(parent_account, '') = '' and docstatus < 2")
		root_acc = [d[0] for d in roots]
		root_orig = ['Application of Funds (Assets)', 'Expenses', 'Income', 'Source of Funds (Liabilities)']
		self.assertEqual(root_acc, root_orig)
		print "Root accounts: %s found" % str(root_acc)
		
		# check nested set model
		for d in roots:
			acc_count = webnotes.conn.sql("select count(name) from `tabAccount` \
				where lft >= %s and rgt <= %s and docstatus < 2", (d[1], d[2]))[0][0]
			self.assertEqual(cint(d[2]), cint(d[1])+(acc_count*2)-1)
		print "Nestedset model properly built for chart of accounts"
		
		
	def test_account_balance(self):
		print "Checking Account Balance"
		acc_count = webnotes.conn.sql("select count(name) from `tabAccount` where docstatus < 2")[0][0]
		acc_bal = webnotes.conn.sql("select count(name) from `tabAccount Balance` \
			where docstatus < 2 group by fiscal_year")[0][0]
		
		self.assertEqual(acc_count*13, acc_bal)
		print "Account Balance created sucessfully"
				
				
	def test_cost_center(self):
		print "Checking cost centers"
		root_cc = webnotes.conn.sql("select cost_center_name from `tabCost Center` \
			where ifnull(parent_cost_center, '') = '' and docstatus < 2")[0][0]
		self.assertEqual(root_cc, 'Root')
		print "Cost Center: %s found" % root_cc
		
		
	def test_global_defaults(self):
		print "Checking Global defaults"
		preset_global_defaults = {
			'fs_imports': '1', 
			'fs_projects': '1', 
			'fs_page_break': '1', 
			'fs_recurring_invoice': '1', 
			'valuation_method': 'FIFO', 
			'fs_quality': '1', 
			'fs_more_info': '1', 
			'currency': 'INR', 
			'fs_packing_details': '1', 
			'stock_uom': 'Nos', 
			'fs_brands': '1', 
			'price_list_currency': '', 
			'fs_sales_extras': '1', 
			'fs_item_serial_nos': '1', 
			'fs_manufacturing': '1', 
			'territory': 'Default', 
			'allow_negative_stock': '', 
			'company': 'Test Company', 
			'fs_item_batch_nos': '1', 
			'customer_group': 'Default Customer Group', 
			'currency_format': 'Lacs', 
			'fs_exports': '1', 
			'fs_after_sales_installations': '1', 
			'maintain_same_rate': '1', 
			'fs_discounts': '1', 
			'supplier_type': 'Default Supplier Type', 
			'cust_master_name': 'Customer Name', 
			'date_format': 'dd-mm-yyyy', 
			'price_list_name': 'Standard', 
			'supp_master_name': 'Supplier Name', 
			'fs_item_group_in_details': '1', 
			'item_group': 'Default', 
			'fraction_currency': '', 
			'account_url': '', 
			'fs_item_advanced': '1', 
			'fs_pos': '1', 
			'fs_purchase_discounts': '1', 
			'fs_item_barcode': '1'
		}
		
		sys_defs = get_defaults()
		
		for d in preset_global_defaults:
			self.assertTrue(sys_defs.has_key(d))
			self.assertEqual(sys_defs.get(d), preset_global_defaults[d])
		print "Global Defaults properly set"
			
	def test_patch_version(self):
		print "Checking patch version"
		pv = webnotes.conn.sql("select defvalue from `tabDefaultValue` \
			where parent = 'Control Panel' and defkey = 'patch_version'")[0][0]
		from patches.patch_list import patch_dict
		self.assertEqual(pv, max(patch_dict.keys()))
		print "Patch version: %s properly updated" % pv
		
	def test_user(self):
		users = [cstr(d[0]) for d in webnotes.conn.sql("select name from `tabProfile` order by name")]
		self.assertEqual(users, ['Administrator', 'All', 'Guest'])
		print "Users: %s found" % users
		
		
	def tearDown(self):
		webnotes.conn.rollback()
		webnotes.conn.close()
		
if __name__ == '__main__':
	unittest.main()