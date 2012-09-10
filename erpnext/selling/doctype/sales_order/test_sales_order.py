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
from webnotes.utils import nowdate, add_days
from webnotes.model import get_controller

base_so = {
	"doctype": "Sales Order",
	"naming_series": "SO",
	"company": "East Wind Corporation",
	"posting_date": nowdate(),
	"party": "Robert Smith",
	"order_type": "Sales",
	"currency": "INR",
	"exchange_rate": 1,
	"price_list": "Standard",
	"price_list_currency": "INR",
	"plc_exchange_rate": 1,
	"__islocal": 1
}

base_so_item = {
	"doctype": "Sales Order Item",
	"parentfield": "sales_order_items",
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

class TestSalesOrder(TestBase):	
	def test_duplicate_sales_order_against_po(self):
		so = base_so.copy()
		so.update({'customer_po': 'PO000001', 'docstatus': 1})
		webnotes.model.insert([so, base_so_item])
		
		so_duplicate = base_so.copy()
		so_duplicate.update({'customer_po': 'PO000001', 'docstatus': 1})
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert, 
			[so_duplicate, base_so_item])
					
	def test_project(self):
		project = {
			'doctype': 'Project', 'name': 'PROJ001', 'status': 'Open',
			'project_name': 'Test Project', 'party': 'Alpha Corporation'
		}
		webnotes.model.insert(project)
		so = base_so.copy()
		so.update({"project_name": project['name']})
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert, \
			[so, base_so_item])
			
	def test_max_discount(self):
		webnotes.conn.set_value('Item', 'Home Desktop 100', 'max_discount', 50)
		so_item = base_so_item.copy()
		so_item.update({"discount": 60})
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert, 
			[base_so, so_item])
			
	def test_exchange_rate(self):
		# exchange rate not specified
		so = base_so.copy()
		so.update({"exchange_rate": ""})
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert, [so, base_so_item])
		
		# exchange rate != 1
		so = base_so.copy()
		so.update({"exchange_rate": 50})
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert, [so, base_so_item])
		
		# price list exchange rate != 1
		so = base_so.copy()
		so.update({"plc_exchange_rate": 50})
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert, [so, base_so_item])
		
		# if diff currency, exchange_rate !=(0, 1)
		webnotes.conn.set_value('Company', base_so['company'], 'default_currency', 'USD')
		self.assertRaises(webnotes.ValidationError, \
			webnotes.model.insert, [base_so, base_so_item])
			
	def test_credit_limit(self):
		webnotes.conn.set_value("Party", "Robert Smith", "credit_limit", 100000)
		so = base_so.copy()
		so.update({'docstatus': 1})
		so_item = base_so_item.copy()
		so_item.update({'rate': 50000})
		self.assertRaises(webnotes.ValidationError, \
			webnotes.model.insert, [so, so_item])
		
	def test_validate_with_quote(self):
		# save quotation
		from selling.doctype.quotation.test_quotation import \
			base_quote, base_quote_item
		quote = base_quote.copy()
		quote.update({'docstatus': 1})
		quote_ctlr = webnotes.model.insert([quote, base_quote_item])

		so = base_so.copy()
		so.update({'docstatus': 1, 'order_type': 'Maintenance'})
		so_item = base_so_item.copy()
		so_item.update({"quotation": quote_ctlr.doc.name, \
			"quotation_item": quote_ctlr.doclist[1].name})
		
		# quotation not submitted		
		self.assertRaises(webnotes.IntegrityError, webnotes.model.insert, 
			[so, so_item])
	
		# so posting date before quote posting date
		so = base_so.copy()
		so.update({'posting_date': add_days(nowdate(), -2), 'docstatus': 1})
		self.assertRaises(webnotes.IntegrityError, webnotes.model.insert, [so, so_item])
	
		# order type not matched
		so = base_so.copy()
		so.update({'docstatus': 1})
		so_item = base_so_item.copy()
		so_item.update({
			"quotation": quote_ctlr.doc.name, 
			"quotation_item": quote_ctlr.doclist[1].name,
			"stock_uom": "Mtr"
		})
		print """testing 1"""
		import pprint
		pprint.pprint(quote_ctlr.doclist[1])
		self.assertRaises(webnotes.IntegrityError, webnotes.model.insert, [so, so_item])
	
	
	def test_taxes_and_totals(self):
		so_item = base_so_item.copy()
		so_item.update({'taxes_and_charges': 'default_taxes'})
		
		so = base_so.copy()
		so.update({"docstatus": 1})
		
		so_ctlr = webnotes.model.insert([so, base_so_item, so_item])
		self.assertEqual(webnotes.conn.get_value('Sales Order', so_ctlr.doc.name, \
			'taxes_and_charges_total'), 55)
		self.assertEqual(webnotes.conn.get_value('Sales Order', so_ctlr.doc.name, \
			'net_total'), 1000)
		self.assertEqual(webnotes.conn.get_value('Sales Order', so_ctlr.doc.name, \
			'grand_total'), 1055)