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
		webnotes.model.insert({
			"doctype": "Lead", "name": "LEAD001", "lead_name": "LEAD001",
			"status": "Open", "naming_series": "LEAD"
		})
		
		cust = base_customer.copy()
		cust['lead_name'] = 'LEAD001'
		webnotes.model.insert(cust, ignore_fields=1)
		self.assertEqual(webnotes.conn.get_value("Lead", "LEAD001", "status"), "Converted")
		
	def test_customer_account(self):
		cust = base_customer.copy()
		cust.update({"credit_days": "90", "credit_limit": "100000"})
		webnotes.model.insert(cust)
		
		self.assertTrue(
			webnotes.conn.get_value("Account", {
				"account_name": "test_customer",
				"parent_account": webnotes.conn.get_value("Company", "East Wind Corporation", "receivables_group"), 
				"master_name": "test_customer", 
				"debit_or_credit": "Debit", 
				"group_or_ledger": "Ledger",
				"credit_days": 90, 
				"credit_limit": 100000
			})
		)
		
	def test_address_and_contact(self):
		webnotes.model.insert({
			"doctype": "Lead", "name": "LEAD001", "lead_name": "Robert Smith",
			"status": "Open", "naming_series": "LEAD", "address_line1": "F/102, 247 Park",
			"mobile_no": "1234567890", "email_id": "email@domain.com"
		})
		
		cust = base_customer.copy()
		cust['lead_name'] = 'LEAD001'
		webnotes.model.insert(cust, ignore_fields=1)
		
		self.assertTrue(
			webnotes.conn.get_value("Address", {
				"customer": "test_customer",
				"address_type": "Office",
				"email_id": "email@domain.com",
				"is_primary_address": 1,
				"name": "test_customer-Office"
			})
		)
		self.assertTrue(
			webnotes.conn.get_value("Contact", {
				"customer": "test_customer",
				"email_id": "email@domain.com",
				"is_primary_contact": 1,
				"first_name": "Robert Smith",
				"name": "Robert Smith-test_customer"
			})
		)

	def test_customer_deletion(self):
		webnotes.model.insert({
			"doctype": "Lead", "name": "LEAD001", "lead_name": "Robert Smith",
			"status": "Open", "naming_series": "LEAD", "address_line1": "F/102, 247 Park",
			"mobile_no": "1234567890", "email_id": "email@domain.com"
		})
		
		cust = base_customer.copy()
		cust['lead_name'] = 'LEAD001'
		webnotes.model.insert(cust, ignore_fields=1)

		webnotes.model.delete_doc('Customer', 'test_customer')
		
		self.assertFalse(webnotes.conn.exists("Account", "test_customer - EW"))
		self.assertFalse(webnotes.conn.exists("Address", "test_customer-Office"))
		self.assertFalse(webnotes.conn.exists("Account", "Robert Smith-test_customer"))
		
		self.assertEqual(webnotes.conn.get_value("Lead", "LEAD001", "status"), "Open")
		
	def test_customer_renaming(self):
		webnotes.model.insert(base_customer, ignore_fields=1)
		
		#from webnotes.model.utils import rename
		from webnotes.model.rename_doc import rename_doc
		rename_doc("Customer", "test_customer", "test_customer_renamed")
		
		self.assertFalse(webnotes.conn.exists("Customer", "test_customer"))
		self.assertTrue(webnotes.conn.exists("Customer", "test_customer_renamed"))
		self.assertTrue(
			webnotes.conn.get_value("Account", {
				"account_name": "test_customer", "master_name": "test_customer_renamed"
			})
		)