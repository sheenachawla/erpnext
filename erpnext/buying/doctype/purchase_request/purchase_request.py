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


# Notes
# For stop / unstop, set status = "Stop"/"Unstop" and save the form

from __future__ import unicode_literals
import webnotes
import webnotes.model
from webnotes.utils import getdate, now_datetime, comma_and, flt
from webnotes.model.controller import DocListController

class PurchaseRequestController(DocListController):
	def validate(self):
		# TODO: DocType Validator: d.schedule_date < self.doc.transaction_date
		# TODO: DocType Validator: if amended_from, amendment_date is mandatory
		# TODO: DocType Validator: d.qty > 0
		
		if self.doc.docstatus != 2: # validation for draft, submit
			self.validate_items()
			self.validate_qty()
		elif self.doc.docstatus == 2: # validation for cancel
			# Check if Purchase Order has been submitted against current Purchase Request
			is_next_submitted("Purchase Order Item", "prevdoc_docname")
			
			# Check if Supplier Quotation has been submitted against current Purchase Request?
			is_next_submitted("Supplier Quotation Item", "prevdoc_docname")
		
		# set status field
		if self.doc.docstatus == 0 and not self.doc.status:
			self.doc.status = "Draft"
		elif self.doc.docstatus == 1 and (not self.doc.status or self.doc.status == "Draft"):
			self.doc.status = "Submitted"
		elif self.doc.docstatus == 2:
			self.doc.status = "Cancelled"
		
	def validate_items(self):
		for child in self.doclist.get({"parentfield": "indent_details"}):
			# get item controller. Also raises error if item not found
			itemcon = webnotes.model.get_controller("Item", child.item_code)

			# check if purchase item
			if itemcon.doc.is_purchase_item != "Yes":
				webnotes.msgprint("""Item "%s" is not a Purchase Item""", raise_exception=1)

			# check if end of life has reached
			if itemcon.doc.end_of_life and getdate(itemcon.doc.end_of_life) <= now_datetime().date():
				import stock
				webnotes.msgprint("""Item "%s" has reached its end of life""",
					raise_exception=stock.ItemEndOfLifeError)

			# check if warehouse is required
			if itemcon.doc.is_stock_item == "Yes" and not child.warehouse:
				webnotes.msgprint("""Warehouse is Mandatory for Item "%s", as it is a Stock Item""" % \
					child.item_code, raise_exception=webnotes.MandatoryError)
	
	def validate_qty(self):
		"""Do not request for more quantity than that in Sales Order"""
		# collate item quantity against sales order
		item_qty_per_so = {}
		for child in self.doclist.get({"parentfield": "indent_details"}):
			if child.sales_order_no:
				so = item_qty_per_so.setdefault(child.sales_order_no, {})
				so[child.item_code] = so.setdefault(child.item_code, 0) + flt(child.qty)
		
		for so in item_qty_per_so:
			# get quantities for all items in a single query
			sales_order_qty = webnotes.conn.sql("""select item_code, sum(ifnull(qty, 0))
				from `tabSales Order Item` where parent = %s and docstatus = 1
				group by item_code""", so)
			
			requested_qty = webnotes.conn.sql("""select item_code, sum(ifnull(qty, 0))
				from `tabPurchase Request Item` where sales_order_no = %s and parent != %s 
				and docstatus = 1 group by item_code""", (so, self.doc.name))
			
			sales_order_qty = sales_order_qty and dict(sales_order_qty) or {}
			requested_qty = requested_qty and dict(requested_qty) or {}
			
			for item in item_qty_per_so[so]:
				# [anandpdoshi]
				# this error will rarely occur as it is fetched through mapper
				# But I thought it would be a good practice to validate it
				# It is not costing any extra query
				if item not in sales_order_qty:
					webnotes.msgprint("""Item "%s" not found in Sales Order "%s" """ % \
						(item, so), raise_exception=webnotes.NameError)
				
				if (flt(item_qty_per_so[so][item]) + flt(requested_qty.get(item))) > \
						flt(sales_order_qty.get(item)):
					import buying
					max_request = flt(sales_order_qty.get(item)) - flt(requested_qty.get(item))
					additional_request = flt(item_qty_per_so[so][item]) - max_request
					webnotes.msgprint("""You can request upto %d "%s" against Sales Order "%s".
						For additional request, add "%s" as a separate row with quantity as %d""" % \
						(max_request, item, so, item, additional_request),
						raise_exception=buying.OverRequestError)
	
	def is_next_submitted(self, childtype, reference_field):
		"""Validate if current doc's next step has already been submitted"""
		submitted = webnotes.conn.sql("""select distinct parent from `tab%s`
			where `%s` = %s and docstatus = 1""", (childtype, reference_field, "%s"), self.doc.name)
		if submitted:
			if len(submitted) > 1:
				webnotes.msgprint("""%s: "%s" has already been submitted""" % \
					(doctype, submitted[0][0]), raise_exception=webnotes.DependencyError)
			else:
				webnotes.msgprint("""%s: %s have already been submitted""" % \
					(doctype, comma_and(["\"%s\"" % d[0] for d in submitted])),
					raise_exception=webnotes.DependencyError)
	