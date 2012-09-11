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
import webnotes.model
from webnotes.tests.test_base import TestBase

base_item_group = {
	"doctype":"Item Group", "parent_item_group":"All Item Groups",
	"is_group": "No"
}

base_item = {
	'doctype': 'Item', 'item_name': 'test_item', 'description': 'Test Item',
	'item_code': 'test_item', 'item_group': 'Home Series', 'is_stock_item': 'Yes', 
	'has_serial_no': 'No', 'stock_uom': 'Nos', 'is_sales_item': 'Yes', 
	'is_purchase_item': 'Yes', 'is_service_item': 'No', 'has_batch_no': 'No',
	'inspection_required': 'No',
}

def load_data(session):
	make_item_groups(session)
	session.insert_test_data("Item")
	
def make_item_groups(session):
	session.insert_test_data("Item Group",
		sort_fn=lambda ig: (ig[0].get('parent_item_group'), ig[0].get('name')))

class TestItem(TestBase):
	def setUp(self):
		super(TestItem, self).setUp()
		make_item_groups(session)
	
	def test_item_creation(self):
		self.session.insert_variants(base_item, [{
			"name":"Home Desktop 1000"
		}])
		self.assertTrue(self.session.db.exists("Item", "Home Desktop 1000"))
		
		# test item creation with autoname
		self.session.insert_variants(base_item, [{
			"item_code": "Home Desktop 2000",
		}])
		self.assertTrue(self.session.db.exists("Item", "Home Desktop 2000"))

	def test_duplicate(self):
		self.session.insert([{"doctype": "Price List", "name": "Retail",
			"price_list_name": "Retail"}])
		
		item = base_item.copy()
		item.update({"name":"Home Desktop 1000"})
		ref_rate_detail = {"doctype":"Item Price", "price_list_name":"Retail", 
			"ref_currency":"INR", "parentfield":"ref_rate_details", "parenttype":"Item"}
		self.assertRaises(webnotes.DuplicateEntryError, self.session.insert, [item, 
			ref_rate_detail, ref_rate_detail])
		
		item = item.copy()
		item["name"] = "Home Desktop 2000"
		self.session.insert([item, ref_rate_detail])
		
	def test_link_validation(self):
		item = base_item.copy()
		
		# expenses is a group
		item.update({"name":"Home Desktop 1000", "purchase_account":"Expenses - EW"})
		self.assertRaises(webnotes.LinkFilterError, self.session.insert, [item])

		# check if link filter error occurs for child item
		item = base_item.copy()
		item["name"] = "Home Desktop 2000"
		item_tax = {
			"doctype": "Item Tax",
			"parenttype": "Item",
			"parentfield": "item_tax",
			"tax_type": "Tax Assets - EW",
			"tax_rate": 10.0
		}
		self.assertRaises(webnotes.LinkFilterError, self.session.insert, [item, item_tax])

		# valid entry
		item["name"] = "Home Desktop 3000"
		item["purchase_account"] = "Miscellaneous Expenses - EW"
		item_tax["tax_type"] = "Sales Promotion Expenses - EW"
		self.session.insert([item, item_tax])
		self.assertTrue(self.session.db.exists("Item", "Home Desktop 3000"))
		
	def test_conditional_validation(self):
		item = base_item.copy()
		
		# check for parent
		# not a stock item but has a serial no
		item.update({
			"name": "Home Desktop 1000",
			"has_serial_no": "Yes",
			"is_stock_item": "No"
		})
		self.assertRaises(webnotes.ConditionalPropertyError, self.session.insert, [item])
		
		# check if error is raised if net weight is specified, but weight uom is not
		item = base_item.copy()
		item.update({
			"name": "Home Desktop 2000",
			"net_weight": 500,
		})
		self.assertRaises(webnotes.ConditionalPropertyError, self.session.insert, [item])
		
		# valid entry
		item = base_item.copy()
		item.update({
			"name": "Home Desktop 3000",
			"has_serial_no": "Yes",
			"is_stock_item": "Yes",
			"has_batch_no": "Yes",
			"net_weight": 500,
			"weight_uom": "Kg"
		})
		self.session.insert([item])
		self.assertTrue(self.session.db.exists("Item", "Home Desktop 3000"))
