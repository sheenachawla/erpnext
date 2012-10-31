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
import unittest
import webnotes
import webnotes.model
from webnotes.utils import nowdate
from accounts.utils import get_fiscal_year

from stock.doctype.purchase_receipt import test_purchase_receipt

company = webnotes.conn.get_default("company")
abbr = webnotes.conn.get_value("Company", company, "abbr")

def load_data():
	test_purchase_receipt.load_data()
		
	webnotes.insert({"doctype": "Account", "account_name": "CST",
		"parent_account": "Direct Expenses - %s" % abbr, "company": company,
		"group_or_ledger": "Ledger"})
	
	# create customer group
	webnotes.insert({"doctype": "Customer Group", "supplier_type": "Retail"})

	# create customer
	webnotes.insert({"doctype": "Customer", "customer_name": "Test Customer",
		"supplier_type": "Retail", "company": company})

		
		
		
import json	
dn_doclist = [
	# parent
	{
		"doctype": "Delivery Note", 
		"supplier_name": "Test Customer",
		"naming_series": "DN", "posting_date": nowdate(),
		"company": company, "fiscal_year": webnotes.conn.get_default("fiscal_year"), 
		"currency": webnotes.conn.get_default("currency"), "conversion_rate": 1,
	},
	# items
	{
		"doctype": "Delivery Note Item", 
		"item_code": "Home Desktop 100", "uom": "Nos", "qty": 10, "rate": 80,
		"amount": 800, "parentfield": "delievry_note_details", "conversion_factor": 1, 
	}
	# taxes
	{
		"doctype": "Sales Taxes and Charges", "charge_type": "On Net Total",
		"account_head": "VAT - Test - %s" % abbr, "rate": 10, "parentfield": "other_charges",
	},
	{
		"doctype": "Purchase Taxes and Charges", "charge_type": "On Net Total",
		"account_head": "CST - %s" % abbr, "rate": 5, "parentfield": "other_charges",
	},
]

class TestDeliveryNote(unittest.TestCase):
	def setUp(self):
		webnotes.conn.begin()
		load_data()
		webnotes.conn.set_value("Global Defaults", None, "automatic_inventory_accounting", 1)

		
	def submit_purchase_receipt(self):
		from webnotes.model.doclist import DocList
		pr = webnotes.insert(DocList(test_purchase_receipt.base_purchase_receipt))
		pr.submit()
		
