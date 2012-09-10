# ERPNext - web based ERP (http://erpnext.com)
# Copyright (C) 2012 Web Notes Technologies Pvt Ltd
# 
# This program is free quoteftware: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free quoteftware Foundation, either version 3 of the License, or
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
from webnotes.utils import nowdate, add_days
from webnotes.model import get_controller

base_quote = {
	"doctype": "Quotation",
	"naming_series": "QTN",
	"company": "East Wind Corporation",
	"posting_date": nowdate(),
	"quotation_to": "Party",
	"party": "Robert Smith",
	"order_type": "Sales",
	"currency": "INR",
	"exchange_rate": 1,
	"price_list_name": "Standard",
	"price_list_currency": "INR",
	"plc_exchange_rate": 1,
	"__islocal": 1
}

base_quote_item = {
	"doctype": "Quotation Item",
	"parentfield": "quotation_items",
	"item_code": "Home Desktop 100",
	"qty": 5,
	"rate": 100,
	"amount": 500,
	"uom": "Nos",
	"item_name": "Home Desktop 100",
	"description": "Home Desktop 100",
	"item_or_tax": "Item",
	"__islocal": 1
}

base_taxes_master = [
	{
		'doctype': 'Taxes and Charges', 'name': 'default_taxes_and_charges', 
		'company': 'East Wind Corporation', 'is_default': 1, "__islocal": 1
	},
	{
		'doctype': 'Taxes and Charges Account', 'parentfield': 'taxes_and_charges_accounts',
		'account': 'Service Tax - EW', 'rate': 10, 
		'description': 'service tax', "__islocal": 1
	},
	{
		'doctype': 'Taxes and Charges Account', 'parentfield': 'taxes_and_charges_accounts',
		'account': 'Miscellaneous Expenses - EW', 'rate': 1,
		'description': 'Miscellaneous Expenses', "__islocal": 1
	}
]

def load_data():
	webnotes.model.insert([{
		"doctype": "Account", "account_name": "Service Tax",
		"parent_account": "Duties and Taxes - EW",
		"group_or_ledger": "Ledger", "debit_or_credit": "Credit",
		"is_pl_account": "No", "company": "East Wind Corporation"
	}])
	return webnotes.model.insert(base_taxes_master)

class TestQuotation(TestBase):
	def test_item_type(self):
		# not sales item
		webnotes.conn.set_value('Item', 'Home Desktop 100', 'is_sales_item', 'No')
		self.assertRaises(webnotes.ValidationError, \
			webnotes.model.insert, [base_quote, base_quote_item])
			
		# not service item
		quote = base_quote.copy()
		quote.update({"order_type": "Maintenance"})
		self.assertRaises(webnotes.ValidationError, \
			webnotes.model.insert, [quote, base_quote_item])
	
	def test_max_discount(self):
		webnotes.conn.set_value('Item', 'Home Desktop 100', 'max_discount', 50)
		quote_item = base_quote_item.copy()
		quote_item.update({"discount": 60})
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert, 
			[base_quote, quote_item])

	def test_exchange_rate(self):
		# exchange rate not specified
		quote = base_quote.copy()
		quote.update({"exchange_rate": ""})
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert, [quote, base_quote_item])

		# exchange rate != 1
		quote = base_quote.copy()
		quote.update({"exchange_rate": 50})
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert, [quote, base_quote_item])

		# price list exchange rate != 1
		quote = base_quote.copy()
		quote.update({"plc_exchange_rate": 50})
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert, [quote, base_quote_item])

		# if diff currency, exchange_rate !=(0, 1)
		webnotes.conn.set_value('Company', base_quote['company'], 'default_currency', 'USD')
		self.assertRaises(webnotes.ValidationError, \
			webnotes.model.insert, [base_quote, base_quote_item])

	def test_order_lost_if_so_exists(self):
		quote = base_quote.copy()
		quote.update({"docstatus": 1})
		
		# success
		quote_ctlr = webnotes.model.insert([quote, base_quote_item])
		
		# exception as submitted so exists
		from selling.doctype.sales_order.test_sales_order import \
			base_so, base_so_item
		so = base_so.copy()
		so.update({"docstatus": 1})
		so_item = base_so_item.copy()
		so_item.update({"quotation": quote_ctlr.doc.name})
		webnotes.model.insert([so, so_item])
		
		quote_ctlr.doc.docstatus = 2
		self.assertRaises(webnotes.ValidationError, quote_ctlr.save)
		
	def test_taxes_and_totals(self):
		taxes_ctlr = load_data()
		quote_item = base_quote_item.copy()
		quote_item.update({'taxes_and_charges': taxes_ctlr.doc.name})
		
		quote = base_quote.copy()
		quote.update({"docstatus": 1})
		
		quote_ctlr = webnotes.model.insert([quote, base_quote_item, quote_item])
		self.assertEqual(webnotes.conn.get_value('Quotation', quote_ctlr.doc.name, \
			'taxes_and_charges_total'), 55)
		self.assertEqual(webnotes.conn.get_value('Quotation', quote_ctlr.doc.name, \
			'net_total'), 1000)
		self.assertEqual(webnotes.conn.get_value('Quotation', quote_ctlr.doc.name, \
			'grand_total'), 1055)