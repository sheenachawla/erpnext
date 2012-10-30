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

company = webnotes.conn.get_default("company")
abbr = webnotes.conn.get_value("Company", company, "abbr")

def load_data():
	# create default warehouse
	if not webnotes.conn.exists("Warehouse", "Default Warehouse"):
		webnotes.model.insert({"doctype": "Warehouse", 
			"warehouse_name": "Default Warehouse",
			"warehouse_type": "Stores"})
	
	# create UOM: Nos.
	if not webnotes.conn.exists("UOM", "Nos"):
		webnotes.model.insert({"doctype": "UOM", "uom_name": "Nos"})
	
	from webnotes.tests import insert_test_data
	# create item groups and items
	insert_test_data("Item Group", 
		sort_fn=lambda ig: (ig[0].get('parent_item_group'), ig[0].get('name')))
	insert_test_data("Item")

	# create supplier type
	webnotes.model.insert({"doctype": "Supplier Type", "supplier_type": "Manufacturing"})
	
	# create supplier
	webnotes.model.insert({"doctype": "Supplier", "supplier_name": "East Wind Inc.",
		"supplier_type": "Manufacturing", "company": company})
		
	# create default cost center if not exists
	if not webnotes.conn.exists("Cost Center", "Default Cost Center - %s" % abbr):
		dl = webnotes.model.insert({"doctype": "Cost Center", "group_or_ledger": "Ledger",
			"cost_center_name": "Default Cost Center", 
			"parent_cost_center": "Root - %s" % abbr,
			"company_name": company, "company_abbr": abbr})
		
	# create account heads for taxes
	
	webnotes.model.insert({"doctype": "Account", "account_name": "Shipping Charges",
		"parent_account": "Stock Expenses - %s" % abbr, "company": company,
		"group_or_ledger": "Ledger"})
		
	webnotes.model.insert({"doctype": "Account", "account_name": "Customs Duty",
		"parent_account": "Stock Expenses - %s" % abbr, "company": company,
		"group_or_ledger": "Ledger"})
	webnotes.model.insert({"doctype": "Account", "account_name": "Tax Assets",
		"parent_account": "Current Assets - %s" % abbr, "company": company,
		"group_or_ledger": "Group"})
	webnotes.model.insert({"doctype": "Account", "account_name": "VAT - Test",
		"parent_account": "Tax Assets - %s" % abbr, "company": company,
		"group_or_ledger": "Ledger"})
		
	# create BOM
	webnotes.model.insert([
		{"doctype": "BOM", "item": "Nebula 7", "quantity": 1,
			"is_active": "Yes", "is_default": 1, "uom": "Nos"},
		{"doctype": "BOM Operation", "operation_no": 1, "parentfield": "bom_operations",
			"opn_description": "Development"}, 
		{"doctype": "BOM Item", "item_code": "Android Jack D", "operation_no": 1, 
			"qty": 5, "rate": 20, "amount": 100, "stock_uom": "Nos", 
			"parentfield": "bom_materials"}
	])


base_purchase_receipt = [
	{
		"doctype": "Purchase Receipt", "supplier": "East Wind Inc.",
		"naming_series": "PR", "posting_date": nowdate(), "posting_time": "12:05",
		"company": company, "fiscal_year": webnotes.conn.get_default("fiscal_year"), 
		"currency": webnotes.conn.get_default("currency"), "exchange_rate": 1
	},
	{
		"doctype": "Purchase Receipt Item", 
		"item_code": "Home Desktop 100",
		"qty": 10, "received_qty": 10, "rejected_qty": 0, "rate": 50, 
		"amount": 500, "warehouse": "Default Warehouse", "item_tax_amount": 250,
		"parentfield": "purchase_receipt_items",
		"conversion_factor": 1, "uom": "Nos", "stock_uom": "Nos"
	},
	{
		"doctype": "Purchase Taxes and Charges", "charge_type": "Actual",
		"account_head": "Shipping Charges - %s" % abbr, "rate": 100, "tax_amount": 100,
		"category": "Valuation and Total", "parentfield": "taxes_and_charges",
		"cost_center": "Default Cost Center - %s" % abbr
	}, 
	{
		"doctype": "Purchase Taxes and Charges", "charge_type": "Actual",
		"account_head": "VAT - Test - %s" % abbr, "rate": 120, "tax_amount": 120,
		"category": "Total", "parentfield": "taxes_and_charges"
	},
	{
		"doctype": "Purchase Taxes and Charges", "charge_type": "Actual",
		"account_head": "Customs Duty - %s" % abbr, "rate": 150, "tax_amount": 150,
		"category": "Valuation", "parentfield": "taxes_and_charges",
		"cost_center": "Default Cost Center - %s" % abbr
	}
]


class TestPurchaseReceipt(unittest.TestCase):
	def setUp(self):
		webnotes.conn.begin()
		load_data()
		webnotes.conn.set_value("Global Defaults", None, "automatic_inventory_accounting", 1)
		
		
	def test_purchase_receipt(self):
		# warehouse does not have stock in hand specified
		self.run_purchase_receipt_test(base_purchase_receipt,
			"Stock In Hand - %s" % (abbr,), 
			"Stock Received But Not Billed - %s" % (abbr,), 750.0)
	
	def run_purchase_receipt_test(self, purchase_receipt, debit_account, 
			credit_account, stock_value):
		from webnotes.model.doclist import DocList	
		dl = webnotes.model.insert(DocList(purchase_receipt))
		dl.submit()
		dl.load_from_db()
						
		gle = webnotes.conn.sql("""select account, ifnull(debit, 0), ifnull(credit, 0)
			from `tabGL Entry` where voucher_no = %s""", dl.doclist[0].name)
		
		gle_map = dict(((entry[0], entry) for entry in gle))
		self.assertEquals(gle_map[debit_account], (debit_account, stock_value, 0.0))
		self.assertEquals(gle_map[credit_account], (credit_account, 0.0, stock_value))
		
	def atest_subcontracting(self):
		pr = base_purchase_receipt.copy()
		pr[1].update({"item_code": "Nebula 7"})
		
		self.run_purchase_receipt_test(pr, 
			"Stock In Hand - %s" % (abbr,), 
			"Stock Received But Not Billed - %s" % (abbr,), 1750.0)
		
	def tearDown(self):
		webnotes.conn.rollback()