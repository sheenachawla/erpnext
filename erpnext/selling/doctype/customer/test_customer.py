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

base_customer_group = {
	"doctype":"Customer Group", "parent_customer_group":"All Customer Groups",
	"is_group": "No"
}

base_territory = {
	"doctype": "Territory", "parent_territory": "Root",
	"is_group": "No"
}

base_customer = {
	"doctype": 'Customer', "customer_name": "test_customer", "default_currency": "INR",
	"default_price_list": "Standard", "territory": "Default Territory",
	"customer_group": "Default Customer Group"
}

def make_customer_groups():
	webnotes.model.insert_variants(base_customer_group, [
		{"name":"Electronics", "parent_customer_group":"Root", "is_group":"Yes"},
			{"name":"Computers", "parent_customer_group":"Electronics", "is_group": "No"},
			{"name":"TV", "parent_customer_group":"Electronics", "is_group": "No"},
			{"name":"Circuits", "parent_customer_group":"Electronics", "is_group": "No"},
		{"name": "Apparel", "parent_customer_group":"Root", "is_group": "No"}
	])


def make_territory():
	webnotes.model.insert_variants(base_territory, [
		{"name":"East", "parent_territory":"Root", "is_group": "No"},
		{"name":"West", "parent_territory":"Root", "is_group": "No"},
		{"name":"North", "parent_territory":"Root", "is_group": "No"},
		{"name":"South", "parent_territory":"Root", "is_group": "No"},
	])
		
class TestCustomer(TestBase):
	def test_customer_creation(self):
		make_customer_groups()
		make_territory()
		
		customer = base_customer.copy()
		customer.update({
			"customer_name":"Modern Electronics", 
			"customer_group": "Computers", "territory": "East"
		})
		webnotes.model.insert(customer)
		self.assertTrue(webnotes.conn.exists("Customer", "Modern Electronics"))
	
		# test customer creation with naming series
		webnotes.conn.set_default("cust_master_name", "Naming Series")
		# without series
		self.assertRaises(webnotes.MandatoryError, webnotes.model.insert, [customer])
		
		# with series
		customer = base_customer.copy()
		customer["naming_series"] = "CUST"
		webnotes.model.insert(customer)
		self.assertEqual(webnotes.conn.get_value("Customer", \
			{"customer_name": "test_customer"}, "name")[:4], "CUST")

	def test_lead_status(self):
		lead = {
			"doctype": "Lead", "name": "LEAD001", "lead_name": "LEAD001",
			"status": "Open", "naming_series": "LEAD"
		}
		webnotes.model.insert(lead)
		
		cust = base_customer.copy()
		cust['lead_name'] = 'LEAD001'
		webnotes.model.insert(cust, ignore_fields=1)
		self.assertEqual(webnotes.conn.get_value("Lead", "LEAD001", "status"), "Converted")
		
	def test