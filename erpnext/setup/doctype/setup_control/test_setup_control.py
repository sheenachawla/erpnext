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
import json
from webnotes.utils import getdate, add_days, get_first_day
from webnotes.tests.test_base import TestBase

def load_data(session):
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
	try:
		session.get_controller("Setup Control", "Setup Control").setup_account(json.dumps(args))
	except Exception, e:
		self.session.db.rollback()
		raise e

class TestAccountSetup(TestBase):
	def setUp(self):
		super(TestAccountSetup, self).setUp()

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
		self.session.get_controller("Setup Control", "Setup Control").setup_account(json.dumps(args))		
		
	def test_setup(self):
		# Currency
		currency = self.session.db.sql("select name from `tabCurrency` where name = 'INR'",
			as_dict=False)[0][0]
		self.assertTrue('INR', currency)
		
		# Company
		comp, abbr = self.session.db.sql("""select name, abbr from `tabCompany`
			where docstatus != 2""", as_dict=False)[0]
		self.assertTrue(comp, 'East Wind Corporation')
		self.assertTrue(abbr, 'EW')
		
		# Fiscal Year		
		fy = self.session.db.sql("""select name, year_start_date from
			`tabFiscal Year` where docstatus != 2""", as_dict=False)[0]
		self.assertTrue(fy[0])
		
		#global def
		self.assertEqual(fy[0], self.session.db.get_defaults('fiscal_year'))
		self.assertEqual(getdate(fy[1]).strftime('%Y-%m-%d'),
			self.session.db.get_defaults('year_start_date'))
		
		yed = add_days(get_first_day(getdate(fy[1]),0,12), -1)
		self.assertEqual(yed, getdate(self.session.db.get_defaults('year_end_date')))
		
		#check root accounts
		root_acc = [d[0] for d in self.session.db.sql("""select account_name 
			from `tabAccount` where ifnull(parent_account, '') = '' and
			docstatus < 2""", as_dict=False)]
		root_orig = ['Application of Funds (Assets)', 'Expenses', 'Income', 'Source of Funds (Liabilities)']
		self.assertEqual(root_acc, root_orig)
		self.assertNsm('Account', 'parent_account', 'group_or_ledger')
				
		# Cost center
		root_cc = self.session.db.sql("""select cost_center_name from 
			`tabCost Center` where ifnull(parent_cost_center, '') = '' and
			docstatus < 2""", as_dict=False)[0][0]
		self.assertEqual(root_cc, 'Root')
		
		self.assertNsm('Cost Center', 'parent_cost_center', 'group_or_ledger')

		# Defaults
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
			'company': 'East Wind Corporation', 
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
		
		sys_defs = self.session.db.get_defaults()
		
		for d in preset_global_defaults:
			self.assertEqual(sys_defs.get(d), preset_global_defaults[d])
			
		#home page
		hp = self.session.db.get_value('Control Panel', None, 'home_page')
		self.assertEqual(hp, 'desktop')

		# Patches
		pv = self.session.db.get_default('patch_version')
		from patches.patch_list import patch_dict
		patches_in_latest_version = len(patch_dict[max(patch_dict.keys())])
		patches_executed_from_latest_version = self.session.db.sql(
			"""select count(*) from `__PatchLog`
			where patch like '%%%s%%'""" % max(patch_dict.keys()),
			as_dict=False)[0][0]
		
		self.assertEqual(patches_in_latest_version, patches_executed_from_latest_version)
		
		# Users
		users = [d[0] for d in self.session.db.sql("""select name from `tabProfile` 
			order by name""", as_dict=False)]
		self.assertEqual(users, ['Administrator', 'Guest'])

