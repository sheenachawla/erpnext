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
	"conversion_rate": 1,
	"price_list_currency": "INR",
	"plc_conversion_rate": 1,
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
	"__islocal": 1
}

class TestSalesOrder(TestBase):
	def test_delivery_date_greater_than_po_date(self):	
		so = base_so.copy()
		so.update({'po_date':add_days(nowdate(), -5), 'delivery_date':add_days(nowdate(), -10)})
		self.assertRaises(webnotes.ValidationError, \
			webnotes.model.insert, [so, base_so_item])
	
	def test_duplicate_sales_order_against_po(self):
		so = base_so.copy()
		so.update({'po_no': 'PO000001'})
		so_ctlr = get_controller([so, base_so_item])
		so_ctlr.submit()
		
		so_duplicate = base_so.copy()
		so_duplicate.update({'po_no': 'PO000001'})
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert, 
			[so_duplicate, base_so_item])
			
	def test_item_type(self):
		# not sales item
		webnotes.conn.set_value('Item', 'Home Desktop 100', 'is_sales_item', 'No')
		self.assertRaises(webnotes.ValidationError, \
			webnotes.model.insert, [base_so, base_so_item])
			
		# not service item
		so = base_so.copy()
		so.update({"order_type": "Maintenance"})
		self.assertRaises(webnotes.ValidationError, \
			webnotes.model.insert, [so, base_so_item])
		
	def test_validate_with_quote(self):
		# to be done after quotation cleanup
		pass
		
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
			
	