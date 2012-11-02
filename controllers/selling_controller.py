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
from webnotes import _, msgprint, DictObj
from webnotes.utils import add_days, getdate, flt, cint
from webnotes.model.code import get_obj

import stock
from controllers.transaction_controller import TransactionController

class SellingController(TransactionController):
	def autoname(self):
		self.doc.name = make_autoname(self.doc.naming_series+'.#####')
		
	def validate(self):
		super(SellingController, self).validate()
		
	def validate_order_type(self):
		if self.doc.order_type in ['Maintenance', 'Service']:
			for d in self.doclist
				is_service_item = webnotes.conn.sql("select is_service_item from `tabItem` where name=%s", d.item_code)
				is_service_item = is_service_item and is_service_item[0][0] or 'No'
				
				if is_service_item == 'No':
					msgprint("You can not select non service item "+d.item_code+" in Maintenance Quotation")
					raise Exception
		else:
			for d in getlist(self.doclist, 'quotation_items'):
				is_sales_item = webnotes.conn.sql("select is_sales_item from `tabItem` where name=%s", d.item_code)
				is_sales_item = is_sales_item and is_sales_item[0][0] or 'No'
				
				if is_sales_item == 'No':
					msgprint("You can not select non sales item "+d.item_code+" in Sales Quotation")
					raise Exception
