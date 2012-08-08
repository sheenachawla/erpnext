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

base_supplier = {
	"doctype": 'Supplier', "supplier_name": "test_supplier", 
	"default_currency": "INR", "supplier_type": "Default Supplier Type"
}

def make_supplier_type():
	webnotes.model.insert_variants({"doctype": "Supplier Type"}, [
		{"name":"Furniture And Fixture"}, {"name": "Consultancy"},
		{"name": "Retailer"}, {"name": "Electronics"}
	])
	
class TestSupplier(TestBase):
	def test_supplier_creation(self):
		make_supplier_type()
		
		supplier = base_supplier.copy()
		supplier.update({"supplier_name":"Apple", "supplier_type": "Electronics"})		
		webnotes.model.insert(supplier)
		self.assertTrue(webnotes.conn.exists("Supplier", "Apple"))
			
		# test supplier creation with naming series
		webnotes.conn.set_default("supp_master_name", "Naming Series")
		# without series
		self.assertRaises(webnotes.MandatoryError, webnotes.model.insert, [supplier])
		
		# with series
		supplier = base_supplier.copy()
		supplier["naming_series"] = "SUPP"
		webnotes.model.insert(supplier)
		self.assertEqual(webnotes.conn.get_value("Supplier", \
			{"supplier_name": "test_supplier"}, "name")[:4], "SUPP")
		
	def test_supplier_account(self):
		cust = base_supplier.copy()
		cust.update({"credit_days": "90"})
		webnotes.model.insert(cust)
		self.assertTrue(
			webnotes.conn.get_value("Account", {
				"account_name": "test_supplier",
				"parent_account": cust['supplier_type'] + ' - EW',
				"master_name": "test_supplier", 
				"debit_or_credit": "Credit", 
				"group_or_ledger": "Ledger",
				"credit_days": "90"
			})
		)
			
	def test_supplier_deletion(self):		
		supp = base_supplier.copy()
		webnotes.model.insert(supp, ignore_fields=1)
		
		webnotes.model.delete_doc('Supplier', 'test_supplier')
		
		self.assertFalse(webnotes.conn.exists("Account", "test_supplier - EW"))
		self.assertFalse(webnotes.conn.exists("Address", "test_supplier-Office"))
		self.assertFalse(webnotes.conn.exists("Account", "Robert Smith-test_supplier"))
		
	def test_supplier_renaming(self):
		webnotes.model.insert(base_supplier, ignore_fields=1)
		
		from webnotes.model.rename_doc import rename_doc
		rename_doc("Supplier", "test_supplier", "test_supplier_renamed")
		
		self.assertFalse(webnotes.conn.exists("Supplier", "test_supplier"))
		self.assertTrue(webnotes.conn.exists("Supplier", "test_supplier_renamed"))
		self.assertTrue(
			webnotes.conn.get_value("Account", {
				"account_name": "test_supplier", "master_name": "test_supplier_renamed"
			})
		)