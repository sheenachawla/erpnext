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

"""
TODO:

* get projected qty from warehouse on posting date
* make maintenance schedule

** validate with quotation thr: posting_date, order_type, submitted


"""

import webnotes
from webnotes import msgprint, _
from webnotes.utils import getdate, cstr
from webnotes.model import get_controller
from controllers.selling import SalesController

class SalesOrderController(SalesController):
	def setup(self):
		self.item_table_fieldname = 'sales_order_items'
		
	def validate(self):
		super(SalesOrderController, self).validate()
		self.validate_po()
		
		if self.doc.docstatus == 1:
			get_controller('Party',self.doc.party).check_credit_limit(
				self.doc.company, self.doc.grand_total * self.doc.exchange_rate)
				
			from core.doctype.doctype_mapper.doctype_mapper import validate_prev_doclist
			validate_prev_doclist('Quotation', 'Sales Order', self.doclist)
	
	def validate_po(self):
		if self.doc.customer_po and self.doc.party:
			so = webnotes.conn.sql("""select name from `tabSales Order`
				where customer_po = %s and docstatus = 1 and party = %s
				and name != %s""", (self.doc.customer_po, self.doc.party, cstr(self.doc.name)))
			if so:
				msgprint(_("""Another Sales Order (%s) exists against same 
					Customer's Purchase Order and Party.""") % so[0]['name'],
					raise_exception=webnotes.ValidationError)
