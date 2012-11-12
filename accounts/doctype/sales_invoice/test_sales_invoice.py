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
	
	# create customer group
	webnotes.insert({"doctype": "Customer Group",
		"customer_group_name": "Default Customer Group",
		"parent_customer_group": "All Customer Groups", "is_group": "No"})
	
	# create customer
	webnotes.insert({"doctype": "Customer", "customer_name": "West Wind Inc.",
		"customer_type": "Company", "territory": "Default",
		"customer_group": "Default Customer Group", "company": company})
	
	webnotes.insert({"doctype": "Account", "account_name": "Excise Duty",
		"parent_account": "Tax Assets - %s" % abbr, "company": company,
		"group_or_ledger": "Ledger"})
	
	webnotes.insert({"doctype": "Account", "account_name": "Education Cess",
		"parent_account": "Tax Assets - %s" % abbr, "company": company,
		"group_or_ledger": "Ledger"})
	
	webnotes.insert({"doctype": "Account", "account_name": "S&H Education Cess",
		"parent_account": "Tax Assets - %s" % abbr, "company": company,
		"group_or_ledger": "Ledger"})
		
	webnotes.insert({"doctype": "Account", "account_name": "CST",
		"parent_account": "Direct Expenses - %s" % abbr, "company": company,
		"group_or_ledger": "Ledger"})
		
	webnotes.insert({"doctype": "Account", "account_name": "Discount",
		"parent_account": "Direct Expenses - %s" % abbr, "company": company,
		"group_or_ledger": "Ledger"})
		
	from webnotes.model.doc import Document
	item = Document("Item", "Home Desktop 100")
	
	# excise duty
	item_tax = item.addchild("item_tax", "Item Tax")
	item_tax.tax_type = "Excise Duty - %s" % abbr
	item_tax.tax_rate = 10
	item_tax.save()

import json	
sales_invoice_doclist = [
	# parent
	{
		"doctype": "Sales Invoice", 
		"debit_to": "West Wind Inc. - %s" % abbr,
		"customer_name": "West Wind Inc.",
		"naming_series": "INV", "posting_date": nowdate(),
		"company": company, "fiscal_year": webnotes.conn.get_default("fiscal_year"), 
		"currency": webnotes.conn.get_default("currency"), "exchange_rate": 1.0,
		"grand_total_print": 0
	},
	# items
	{
		"doctype": "Sales Invoice Item", "warehouse": "Default Warehouse",
		"item_code": "Home Desktop 100", "qty": 10, "print_rate": 50,
		"parentfield": "sales_invoice_items",
		"uom": "Nos", "item_tax_rate": json.dumps({"Excise Duty - %s" % abbr: 10})
	},
	{
		"doctype": "Sales Invoice Item", "warehouse": "Default Warehouse",
		"item_code": "Home Desktop 200", "qty": 5, "print_rate": 150,
		"parentfield": "sales_invoice_items",
		"uom": "Nos"
	},
	# taxes
	{
		"doctype": "Sales Taxes and Charges", "charge_type": "Actual",
		"account_head": "Shipping Charges - %s" % abbr, "rate": 100, 
		"parentfield": "taxes_and_charges",
		"cost_center": "Default Cost Center - %s" % abbr
	},
	{
		"doctype": "Sales Taxes and Charges", "charge_type": "On Net Total",
		"account_head": "Customs Duty - %s" % abbr, "rate": 10,
		"parentfield": "taxes_and_charges",
		"cost_center": "Default Cost Center - %s" % abbr
	},
	{
		"doctype": "Sales Taxes and Charges", "charge_type": "On Net Total",
		"account_head": "Excise Duty - %s" % abbr, "rate": 12,
		"parentfield": "taxes_and_charges"
	},
	{
		"doctype": "Sales Taxes and Charges", "charge_type": "On Previous Row Amount",
		"account_head": "Education Cess - %s" % abbr, "rate": 2, "row_id": 3,
		"parentfield": "taxes_and_charges"
	},
	{
		"doctype": "Sales Taxes and Charges", "charge_type": "On Previous Row Amount",
		"account_head": "S&H Education Cess - %s" % abbr, "rate": 1, "row_id": 3,
		"parentfield": "taxes_and_charges"
	},
	{
		"doctype": "Sales Taxes and Charges", "charge_type": "On Previous Row Total",
		"account_head": "CST - %s" % abbr, "rate": 2, "row_id": 5,
		"parentfield": "taxes_and_charges",
		"cost_center": "Default Cost Center - %s" % abbr
	},
	{
		"doctype": "Sales Taxes and Charges", "charge_type": "On Net Total",
		"account_head": "VAT - Test - %s" % abbr, "rate": 12.5,
		"parentfield": "taxes_and_charges"
	},
	{
		"doctype": "Sales Taxes and Charges", "charge_type": "On Previous Row Total",
		"account_head": "Discount - %s" % abbr, "rate": -10, "row_id": 7,
		"parentfield": "taxes_and_charges",
		"cost_center": "Default Cost Center - %s" % abbr
	},
]

class TestSalesInvoice(unittest.TestCase):
	def setUp(self):
		webnotes.conn.begin()
		load_data()
		webnotes.conn.set_value("Global Defaults", None, "automatic_inventory_accounting", 1)

	def test_purchase_invoice(self):
		from webnotes.model.doclist import DocList
		controller = webnotes.insert(DocList(sales_invoice_doclist))
		controller.load_from_db()
		dl = controller.doclist

		# test net total
		self.assertEqual(dl[0].net_total, 1250)
		
		# test item values calculation
		expected_values = [
			{
				"item_code": "Home Desktop 100",
				"print_ref_rate": 50,
				"discount": 0,
				"print_amount": 500,
				"ref_rate": 50,
				"rate": 50,
				"amount": 500
			},
			{
				"item_code": "Home Desktop 200",
				"print_ref_rate": 150,
				"discount": 0,
				"print_amount": 750,
				"ref_rate": 150,
				"rate": 150,
				"amount": 750
			},
		]
		for i, item in enumerate(dl.get({"parentfield": "sales_invoice_items"})):
			for key, val in expected_values[i].items():
				self.assertEqual(item.fields.get(key), val)
		
		# test tax amounts and totals
		expected_values = [
			["Shipping Charges - %s" % abbr, 100, 1350],
			["Customs Duty - %s" % abbr, 125, 1475],
			["Excise Duty - %s" % abbr, 140, 1615],
			["Education Cess - %s" % abbr, 2.8, 1617.8],
			["S&H Education Cess - %s" % abbr, 1.4, 1619.2],
			["CST - %s" % abbr, 32.38, 1651.58],
			["VAT - Test - %s" % abbr, 156.25, 1807.83],
			["Discount - %s" % abbr, -180.78, 1627.05],
		]		
		for i, tax in enumerate(dl.get({"parentfield": "taxes_and_charges"})):
			# print tax.account_head, tax.tax_amount, tax.total
			self.assertEqual(tax.account_head, expected_values[i][0])
			self.assertEqual(tax.tax_amount, expected_values[i][1])
			self.assertEqual(tax.total, expected_values[i][2])
	
	def test_purchase_invoice_with_inclusive_tax(self):
		sales_invoice_doclist[1]["print_rate"] = 62.683
		sales_invoice_doclist[2]["print_rate"] = 191
		for i in [3, 5, 6, 7, 8, 9]:
			print sales_invoice_doclist[i]["charge_type"]
			sales_invoice_doclist[i]["included_in_print_rate"] = 1
		
		from webnotes.model.doclist import DocList
		controller = webnotes.insert(DocList(sales_invoice_doclist))
		controller.load_from_db()
		dl = controller.doclist

		# test item values calculation
		expected_values = [
			{
				"item_code": "Home Desktop 100",
				"print_ref_rate": 62.683,
				"discount": 0,
				"print_amount": 626.83,
				"ref_rate": 50,
				"rate": 50,
				"amount": 500
			},
			{
				"item_code": "Home Desktop 200",
				"print_ref_rate": 191,
				"discount": 0,
				"print_amount": 956,
				"ref_rate": 150,
				"rate": 150,
				"amount": 750
			},
		]
		for i, item in enumerate(dl.get({"parentfield": "sales_invoice_items"})):
			for key, val in expected_values[i].items():
				self.assertEqual(item.fields.get(key), val)
		
		# test tax amounts and totals
		expected_values = [
			["Shipping Charges - %s" % abbr, 100, 1350, 100, 1682.83],
			["Customs Duty - %s" % abbr, 125, 1475, 125, 1807.83],
			["Excise Duty - %s" % abbr, 140, 1615, 0, 1807.83],
			["Education Cess - %s" % abbr, 2.8, 1617.8, 0, 1807.83],
			["S&H Education Cess - %s" % abbr, 1.4, 1619.2, 0, 1807.83],
			["CST - %s" % abbr, 32.38, 1651.58, 0, 1807.83],
			["VAT - Test - %s" % abbr, 156.25, 1807.83, 0, 1807.83],
			["Discount - %s" % abbr, -180.78, 1627.05, -180.78, 1627.05],
		]		
		for i, tax in enumerate(dl.get({"parentfield": "taxes_and_charges"})):
			print tax.account_head, tax.tax_amount, tax.total, tax.tax_amount_print, tax.total_print
			self.assertEqual(tax.account_head, expected_values[i][0])
			self.assertEqual(tax.tax_amount, expected_values[i][1])
			self.assertEqual(tax.total, expected_values[i][2])
			self.assertEqual(tax.tax_amount_print, expected_values[i][3])
			self.assertEqual(tax.total_print, expected_values[i][4])
			
		# test net total
		self.assertEqual(dl[0].net_total, 1250)
		self.assertEqual(dl[0].net_total_print, 1582.83)

		# # test grand total
		self.assertEqual(dl[0].grand_total, 1627.05)
		self.assertEqual(dl[0].grand_total_print, 1627.05)
	
	
	
	
	# 		
	# def test_purchase_invoice_having_zero_amount_items(self):
	# 	from webnotes.model.doclist import DocList
	# 	sample_purchase_invoice_doclist = [] + purchase_invoice_doclist
	# 	
	# 	# set rate and amount as 0
	# 	sample_purchase_invoice_doclist[1]["rate"] = 0
	# 	sample_purchase_invoice_doclist[1]["amount"] = 0
	# 	sample_purchase_invoice_doclist[2]["rate"] = 0
	# 	sample_purchase_invoice_doclist[2]["amount"] = 0
	# 	
	# 	
	# 	controller = webnotes.insert(DocList(sample_purchase_invoice_doclist))
	# 	controller.load_from_db()
	# 	dl = controller.doclist
	# 	
	# 	# test net total
	# 	self.assertEqual(dl[0].net_total, 0)
	# 	
	# 	# test tax amounts and totals
	# 	expected_values = [
	# 		["Shipping Charges - %s" % abbr, 100, 100],
	# 		["Customs Duty - %s" % abbr, 0, 100],
	# 		["Excise Duty - %s" % abbr, 0, 100],
	# 		["Education Cess - %s" % abbr, 0, 100],
	# 		["S&H Education Cess - %s" % abbr, 0, 100],
	# 		["CST - %s" % abbr, 2, 102],
	# 		["VAT - Test - %s" % abbr, 0, 102],
	# 		["Discount - %s" % abbr, -10.2, 91.8],
	# 	]
	# 	for i, tax in enumerate(dl.get({"parentfield": "taxes_and_charges"})):
	# 		# print tax.account_head, tax.tax_amount, tax.total
	# 		self.assertEqual(tax.account_head, expected_values[i][0])
	# 		self.assertEqual(tax.tax_amount, expected_values[i][1])
	# 		self.assertEqual(tax.total, expected_values[i][2])
	# 	
	# 	# test item tax amount
	# 	expected_values = [
	# 		["Home Desktop 100", 0],
	# 		["Home Desktop 200", 0]
	# 	]
	# 	for i, item in enumerate(dl.get({"parentfield": "purchase_invoice_items"})):
	# 		self.assertEqual(item.item_code, expected_values[i][0])
	# 		self.assertEqual(item.valuation_tax_amount, expected_values[i][1])
	# 	
	# def test_gl_entries(self):
	# 	from webnotes.model.doclist import DocList
	# 	controller = webnotes.insert(DocList(purchase_invoice_doclist))
	# 	controller.submit()
	# 	controller.load_from_db()
	# 	dl = controller.doclist
	# 	
	# 	expected_values = {
	# 		"West Wind Inc. - %s" % abbr : [0, 1512.30],
	# 		"Shipping Charges - %s" % abbr : [100, 0],
	# 		"Excise Duty - %s" % abbr : [140, 0],
	# 		"Education Cess - %s" % abbr : [2.8, 0],
	# 		"S&H Education Cess - %s" % abbr : [1.4, 0],
	# 		"CST - %s" % abbr : [29.88, 0],
	# 		"VAT - Test - %s" % abbr : [156.25, 0],
	# 		"Discount - %s" % abbr : [0, 168.03],
	# 		"Stock Received But Not Billed - %s" % abbr : [1475, 0],
	# 		"Expenses Included In Valuation - %s" % abbr : [0, 225]
	# 	}
	# 	gl_entries = webnotes.conn.sql("""select account, debit, credit from `tabGL Entry`
	# 		where voucher_type = 'Purchase Invoice' and voucher_no = %s""", dl[0].name, as_dict=1)
	# 	for d in gl_entries:
	# 		self.assertEqual(d["debit"], expected_values.get(d['account'])[0])
	# 		self.assertEqual(d["credit"], expected_values.get(d['account'])[1])
	# 		
		
	def tearDown(self):
		webnotes.conn.rollback()