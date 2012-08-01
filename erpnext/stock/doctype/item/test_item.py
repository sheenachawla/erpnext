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
import webnotes.model
from webnotes.tests.test_base import TestBase

base_item_group = {
	"doctype":"Item Group", "parent_item_group":"All Item Groups",
	"is_group": "No"
}

base_item = {
	'doctype': 'Item', 'item_name': 'test_item', 
	'item_code': 'test_item', 'item_group': 'Default', 'is_stock_item': 'Yes', 
	'has_serial_no': 'No', 'stock_uom': 'Nos', 'is_sales_item': 'Yes', 'is_purchase_item': 'Yes', 
	'is_service_item': 'No'
}

def make_item_groups():
	webnotes.model.insert_variants(base_item_group, [
		{"name":"Desktops", "is_group":"Yes"},
			{"name":"Home Series", "parent_item_group":"Desktops"},
			{"name":"Pro Series", "parent_item_group":"Desktops"},
			{"name":"Gaming Series", "parent_item_group":"Desktops"},
		{"name":"Laptops", "is_group":"Yes"},
			{"name":"Designer Series", "parent_item_group":"Laptops"},
			{"name":"Netbook Series", "parent_item_group":"Laptops"},
			{"name":"Ultrabook Series", "parent_item_group":"Laptops"},
		{"name":"Tablets", "is_group":"Yes"},
			{"name":"7 inch Series", "parent_item_group":"Tablets"},
			{"name":"8 inch Series", "parent_item_group":"Tablets"},
			{"name":"9 inch Series", "parent_item_group":"Tablets"},
		{"name":"Accessories", "is_group":"Yes"},
			{"name":"Laptop Bag", "parent_item_group":"Accessories"},
			{"name":"Tablet Cover", "parent_item_group":"Accessories"},
			{"name":"Mouse", "parent_item_group":"Accessories"},
			{"name":"Peripherals", "parent_item_group":"Accessories"},
		{"name":"Services", "is_group":"Yes"},
			{"name":"Warranty Plan", "parent_item_group":"Services"},
			{"name":"Repairs", "parent_item_group":"Services"},
			{"name":"Website Development", "parent_item_group":"Services"},
	])
		
class TestItem(TestBase):
	def test_item_creation(self):
		make_item_groups()
		webnotes.model.insert_variants(base_item, [{
			"name":"Home Desktop 100"
		}])
		self.assertTrue(webnotes.conn.exists("Item", "Home Desktop 100"))
		
		# test item creation with autoname
		webnotes.model.insert_variants(base_item, [{
			"item_code": "Home Desktop 200"
		}])
		self.assertTrue(webnotes.conn.exists("Item", "Home Desktop 200"))

	def test_duplicate(self):
		item = base_item.copy()
		item.update({"name":"Home Desktop 100"})
		ref_rate_detail = {"doctype":"Item Price", "price_list_name":"Retail", 
			"ref_currency":"INR", "parentfield":"ref_rate_details", "parenttype":"Item"}
		self.assertRaises(webnotes.DuplicateEntryError, webnotes.model.insert, [item, 
			ref_rate_detail, ref_rate_detail])
		
		item = item.copy()
		item["name"] = "Home Desktop 200"
		webnotes.model.insert([item, ref_rate_detail])
		
	def test_link_validation(self):
		item = base_item.copy()
		
		# expenses is a group
		item.update({"name":"Home Desktop 100", "purchase_account":"Expenses - EW"})
		self.assertRaises(webnotes.LinkFilterError, webnotes.model.insert, [item])

		# check if link filter error occurs for child item
		item = base_item.copy()
		item["name"] = "Home Desktop 200"
		item_tax = {
			"doctype": "Item Tax",
			"parenttype": "Item",
			"parentfield": "item_tax",
			"tax_type": "Tax Assets - EW",
			"tax_rate": 10.0
		}
		self.assertRaises(webnotes.LinkFilterError, webnotes.model.insert, [item, item_tax])

		# valid entry
		item["name"] = "Home Desktop 300"
		item["purchase_account"] = "Miscellaneous Expenses - EW"
		item_tax["tax_type"] = "Sales Promotion Expenses - EW"
		webnotes.model.insert([item, item_tax])
		self.assertTrue(webnotes.conn.exists("Item", "Home Desktop 300"))
		
	def test_conditional_validation(self):
		item = base_item.copy()
		
		# check for parent
		# not a stock item but has a serial no
		item.update({
			"name": "Home Desktop 100",
			"has_serial_no": "Yes",
			"is_stock_item": "No"
		})
		self.assertRaises(webnotes.ConditionalPropertyError, webnotes.model.insert, [item])
		
		# check if error is raised if net weight is specified, but weight uom is not
		item = base_item.copy()
		item.update({
			"name": "Home Desktop 200",
			"net_weight": 500
		})
		self.assertRaises(webnotes.ConditionalPropertyError, webnotes.model.insert, [item])
		
		# valid entry
		item = base_item.copy()
		item.update({
			"name": "Home Desktop 300",
			"has_serial_no": "Yes",
			"is_stock_item": "Yes",
			"has_batch_no": "Yes",
			"net_weight": 500,
			"weight_uom": "Kgs"
		})
		webnotes.model.insert([item])
		self.assertTrue(webnotes.conn.exists("Item", "Home Desktop 300"))
