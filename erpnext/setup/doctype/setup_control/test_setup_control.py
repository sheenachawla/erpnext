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
from webnotes.utils import get_defaults, getdate, add_days, get_first_day
from tests.test_base import TestBase

class TestAccountSetup(TestBase):
	def test_default_records(self):
		currency = webnotes.conn.sql("select name from `tabCurrency` where name = 'INR'")[0][0]
		self.assertTrue('INR', currency)
		
	def test_company_record(self):
		comp, abbr = webnotes.conn.sql("select name, abbr from `tabCompany` where docstatus != 2")[0]
		self.assertTrue(comp, 'East Wind Corporation')
		self.assertTrue(abbr, 'EW')
		
	def test_fiscal_year(self):
		fy = webnotes.conn.sql("select name, year_start_date from \
			`tabFiscal Year` where docstatus != 2")[0]
		self.assertTrue(fy[0])
		
		period_count = webnotes.conn.sql("select count(name) from `tabPeriod` \
			where fiscal_year = %s and docstatus != 2", fy[0])[0][0]
		self.assertTrue(period_count, 13)
		
		#global def
		self.assertEqual(fy[0], get_defaults('fiscal_year'))
		self.assertEqual(getdate(fy[1]).strftime('%Y-%m-%d'), get_defaults('year_start_date'))
		
		yed = add_days(get_first_day(getdate(fy[1]),0,12), -1)
		self.assertEqual(yed, get_defaults('year_end_date'))
		
	def test_chart_of_account(self):
		#check root accounts
		root_acc = [d[0] for d in webnotes.conn.sql("select account_name from `tabAccount` \
			where ifnull(parent_account, '') = '' and docstatus < 2")]
		root_orig = ['Application of Funds (Assets)', 'Expenses', 'Income', 'Source of Funds (Liabilities)']
		self.assertEqual(root_acc, root_orig)
				
	def test_account_balance(self):
		acc_count = webnotes.conn.sql("select count(name) from `tabAccount` where docstatus < 2")[0][0]
		acc_bal = webnotes.conn.sql("select count(name) from `tabAccount Balance` \
			where docstatus < 2 group by fiscal_year")[0][0]
		
		self.assertEqual(acc_count*13, acc_bal)
		
		self.assertNsm('Account', 'parent_account', 'group_or_ledger')
				
	def test_cost_center(self):
		root_cc = webnotes.conn.sql("select cost_center_name from `tabCost Center` \
			where ifnull(parent_cost_center, '') = '' and docstatus < 2")[0][0]
		self.assertEqual(root_cc, 'Root')
		
		self.assertNsm('Cost Center', 'parent_cost_center', 'group_or_ledger')
		
	def test_global_defaults(self):
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
		
		sys_defs = get_defaults()
		
		for d in preset_global_defaults:
			self.assertTrue(sys_defs.has_key(d))
			self.assertEqual(sys_defs.get(d), preset_global_defaults[d])
			
		#home page
		hp = webnotes.conn.get_value('Control Panel', None, 'home_page')
		self.assertEqual(hp, 'desktop')
					
	def test_patches(self):
		pv = webnotes.conn.get_default('patch_version')
		from patches.patch_list import patch_dict
		patches_in_latest_version = len(patch_dict[max(patch_dict.keys())])
		patches_executed_from_latest_version = webnotes.conn.sql("select count(*) from `__PatchLog`\
			where patch like '%%%s%%'" % max(patch_dict.keys()))[0][0]
		
		self.assertEqual(patches_in_latest_version, patches_executed_from_latest_version)
		
	def test_user(self):
		users = [d[0] for d in webnotes.conn.sql("select name from `tabProfile` order by name")]
		self.assertEqual(users, ['Administrator', 'Guest'])

