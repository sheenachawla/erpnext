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


# TODO
# source and/or target warehouse mandatory as per stock entry type
# validate approving authority
# validate serial no as per stock entry type
# update serial no status
# maintain 

from __future__ import unicode_literals
import webnotes
from webnotes.utils import cstr, flt, getdate, now
from webnotes import msgprint
from controllers.stock import StockController

class StockEntryController(StockController):
	def setup(self):
		self.item_table_fieldname = 'stock_entry_items'
		
	def validate(self):
		return
		self.validate_max_discount()
		self.validate_exchange_rate()
		self.validate_project()
		self.calculate_totals()
		
		if self.doc.docstatus == 1 and self.doc.stock_entry_type == 'Delivery Note':
			self.check_credit_limit()


	def check_credit_limit(self):
		"""check credit limit for items which are not fetched from sales order"""
		amount = sum([d.amount+d.tax_amount for d in self.doclist.get({\
			'parentfield': 'stock_entry_items'}) if not d.sales_order])
		get_controller('Party',self.doc.party).check_credit_limit(self.doc.company, amount)
