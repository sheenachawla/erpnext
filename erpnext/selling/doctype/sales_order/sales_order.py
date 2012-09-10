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
* get_item_details
* validate_approving_authority

* DocTypeValidator: 
**	If order_type is Sales, Expected Delivery Date is mandatory
**	If amend_from, amendment_date is mandatory
**	Expected Delivery Date cannot be before Posting Date
** validate with quotation thr: posting_date, order_type, submitted


"""

import webnotes
from webnotes import msgprint
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
			get_controller('Party',self.doc.party).check_credit_limit\
				(self.doc.company, self.doc.grand_total)
		
	def on_update(self):
		if self.doc.docstatus == 2:
			self.check_if_nextdoc_exists(['Delivery Note Item', 'Sales Invoice Item', \
				'Maintenance Schedule Item', 'Maintenance Visit Purpose'])
			
	def validate_po(self):
		if self.doc.po_date and self.doc.delivery_date \
			and getdate(self.doc.po_date) > getdate(self.doc.delivery_date):
			msgprint("Expected Delivery Date cannot be before Purchase Order Date", 
				raise_exception=webnotes.MandatoryError)

		if self.doc.po_no and self.doc.party:
			so = webnotes.conn.sql("select name from `tabSales Order` \
				where ifnull(po_no, '') = %s and name != %s and docstatus < 2\
				and party = %s", (self.doc.po_no, cstr(self.doc.name), self.doc.party))
			if so:
				msgprint("""Another Sales Order (%s) exists against same PO No and Party. 
					Please be sure, you are not making duplicate entry.""" % 
					so[0]['name'], raise_exception=webnotes.ValidationError)