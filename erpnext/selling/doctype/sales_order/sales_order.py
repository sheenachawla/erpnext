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
* DocTypeValidator: 
**	If order_type is Sales, Expected Delivery Date is mandatory
**	If amend_from, amendment_date is mandatory
**	Expected Delivery Date cannot be before Posting Date

"""

from __future__ import unicode_literals
import webnotes
from webnotes import msgprint
from webnotes.model import get_controller
from selling.utils import SalesController

class SalesOrderController(SalesController):
	def setup(self):
		self.item_table_filedname = 'sales_order_details'
		
	def validate(self):		
		self.validate_items()
		self.validate_po()
		self.validate_project()
		self.validate_conversion_rate()
		self.validate_max_discount()
		self.validate_sales_team_contribution()

	def validate_po(self):
		if self.doc.po_date and self.doc.delivery_date 
			and getdate(self.doc.po_date) > getdate(self.doc.delivery_date):
			msgprint("Expected Delivery Date cannot be before Purchase Order Date"
				, raise_exception=webnotes.MandatoryError)

		if self.doc.po_no and self.doc.customer:
			so = webnotes.conn.sql("select name from `tabSales Order` \
				where ifnull(po_no, '') = %s and name != %s and docstatus < 2\
				and customer = %s", (self.doc.po_no, self.doc.name, self.doc.customer))
			if so and so[0]['name']:
				msgprint("""Another Sales Order (%s) exists against same PO No and Customer. 
					Please be sure, you are not making duplicate entry.""" % so[0]['name'])

	def validate_items(self):
		quotations = []
		for d in getlist(self.doclist, 'sales_order_details'):
			#TODO: get projected qty
			self.validate_item_type()
			if d.prevdoc_docname and d.prevdoc_docname not in quotations:
				quotations.append(d.prevdoc_docname)				
		self.validate_with_quotation(quotations)
				
	def validate_item_type(self, item_code):
		item_type = webnotes.conn.get_value('Item', item_code, \
			['is_sales_item', 'is_service_item'], as_dict=1)
		if order_type['is_sales_item'] == 'No' and item_type['is_service_item'] == 'No':
			msgprint("Item: %s is neither Sales nor Service Item"
				%item_code, raise_exception=webnotes.ValidationError)
		elif self.doc.order_type == 'Sales' and item_type['is_service_item'] == 'Yes':
			msgprint("Maintenance item can not be selected if order type is 'Sales'"
				, raise_exception=webnotes.ValidationError)
		elif self.doc.order_type == 'Maintenance' and order_type['is_sales_item'] == 'Yes':
			msgprint("Sales item can not be selected if order type is 'Maintenance'"
				, raise_exception=webnotes.ValidationError)
		
	def validate_with_quotation(self, quotations):
		for quotation_no in quotations:
			quote = webnotes.conn.get_value('Quotation', quotation_no, \
				['posting_date', 'order_type', 'docstatus'])
			if quote['posting_date'] > getdate(self.doc.posting_date):
				msgprint("Sales Order Posting Date cannot be before Quotation Posting Date"
					, raise_exception=webnotes.ValidationError)
			if quote['order_type'] != self.doc.order_type:
				msgprint("Order type is not matching with quotation: %s"
				 	% quotation_no, raise_exception=webnotes.ValidationError)
			if quote['docstatus'] != 1:
				msgprint("Quotation: %s is not submitted"
					, raise_exception=webnotes.ValidationError)
		
	def validate_project(self):
		if self.doc.project_name:
			if webnotes.conn.get_value('Project', self.doc.project_name, \
					'customer') !=  self.doc.party:
				msgprint("Project: %s does not associate with party: %s" 
					% (self.doc.project_name, self.doc.party), 
					raise_exception=webnotes.ValidationError)

	def on_submit(self):
		get_controller('Party',self.doc.party).check_credit_limit\
			(self.doc.company, self.doc.grand_total)
		get_controller('Authorization Control').validate_approving_authority\
			(self.doc.doctype, self.doc.grand_total, self)

	def on_cancel(self):
		self.check_if_nextdoc_exists(['Delivery Note Item', 'Sales Invoice Item', \
			'Maintenance Schedule Item', 'Maintenance Visit Purpose'])
			
	def stop_sales_order(self):
		self.doc.stopped = 1
		self.save()
		msgprint("Stopped! To make transactions against this you need to Unstop it.")

	def unstop_sales_order(self):
		self.doc.stopped = 0
		self.save()
		msgprint("Unstopped!")
