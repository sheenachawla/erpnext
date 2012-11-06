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
from webnotes.utils import cint, flt

from controllers.buying_controller import BuyingController

class DocType(BuyingController):
	def setup(self):
		self.item_table_field = "supplier_quotation_items"

	
	# def validate(self):
	# 	super(DocType, self).validate()
	# 	self.validate_schedule_date()
	# 	
	# 	if self.doc.docstatus == 1:
	# 		self.stop_resume_transaction()
	# 		
	# 	self.validate_qty_against_sales_order()
	# 	
	# def on_submit(self):
	# 	super(DocType, self).on_submit()
	# 	self.update_bin()
	# 	
	# def on_cancel(self):
	# 	super(DocType, self).on_cancel()
	# 	if not cint(webnotes.conn.get_value(self.doc.doctype, self.doc.name, "is_stopped")):
	# 		self.update_bin()
	# 
	# 	# if a stopped transaction is cancelled,
	# 	# then, when a user tries to amend the transaction,
	# 	# the amended transaction has is_stopped=1, which should not be the case
	# 	if self.doc.is_stopped == 1:
	# 		webnotes.conn.set(self.doc, "is_stopped", 0)		
	# 	
	# def on_trash(self):
	# 	pass
	# 	
	# def set_item_defaults(self):
	# 	"""set schedule date and min order qty"""
	# 	self.set_schedule_date()
	# 	
	# 	for item in self.doclist.get({"parentfield": "purchase_request_items"}):
	# 		item.min_order_qty = flt(webnotes.conn.get_value("Item", item.item_code,
	# 			"min_order_qty"), self.precision.item.min_order_qty) or 0
	# 			
	# def update_item_details(self):
	# 	"""updates item details, if value is missing"""
	# 	for item in self.doclist.get({"parentfield": "purchase_request_items"}):
	# 		if item.item_code:
	# 			result = self.get_item_details(self, {"item_code": item.item_code,
	# 				"warehouse": item.warehouse})
	# 			for field, val in result.items():
	# 				if not item.get(field):
	# 					item[field] = val
	# 
	# def pull_sales_order_items(self):
	# 	if self.doc.sales_order:
	# 		mapper = get_obj("DocType Mapper", "Sales Order-Purchase Request")
	# 		
	# 		import json
	# 		from_to_list = [["Sales Order", "Purchase Request"],
	# 			["Sales Order Item", "Purchase Request Item"]]
	# 		
	# 		mapper.dt_map("Sales Order", "Purchase Request", self.doc.sales_order,
	# 			self.doc, self.doclist, json.dumps(from_to_list))
	# 
	# 		self.set_item_defaults()
	# 
	# def update_bin(self):
	# 	"""update quantity requested for purchase in bin"""
	# 	for item in self.doclist.get({"parentfield": "purchase_request_items"}):
	# 		if webnotes.conn.get_value("Item", item.item_code, "is_stock_item") == "Yes":
	# 			# bin exists only for a stock item
	# 			if not item.warehouse:
	# 				# bin is a unique combination of (warehouse, item_code)
	# 				msgprint(_("""Row # %(idx)s [Item: %(item_code)s]:
	# 					Warehouse mandatory for a stock item.""") % {
	# 						"idx": item.idx,
	# 						"item_code": item.item_code,
	# 					}, raise_exception=True)
	# 			
	# 			# calculate quantity to be updated in bin
	# 			item.qty = flt(item.qty, self.precision.item.qty)
	# 			item.ordered_qty = flt(item.ordered_qty, self.precision.item.ordered_qty)
	# 			if item.qty > item.ordered_qty:
	# 				qty = flt(item.qty - item.ordered_qty, self.precision.item.qty)
	# 			else:
	# 				qty = 0
	# 			
	# 			# if submit and not stopped, then +ve, else -ve
	# 			qty *= (self.doc.docstatus == 1 and self.doc.is_stopped != 1) and 1 or -1					
	# 
	# 			# finally, update the requested qty
	# 			get_obj("Warehouse", item.warehouse).update_bin({
	# 				"item_code": item.item_code,
	# 				"indented_qty": qty,
	# 				"posting_date": self.doc.posting_date
	# 			})
	# 			
	# def validate_schedule_date(self):
	# 	for item in self.doclist.get({"parentfield": "purchase_request_items"}):
	# 		if item.schedule_date < self.doc.posting_date:
	# 			doctypelist = webnotes.get_doctype(self.doc.doctype)
	# 			msgprint(_("""Row # %(idx)s [Item: %(item_code)s]: 
	# 				%(schedule_date)s cannot be before %(posting_date)s""") % {
	# 				"idx": item.idx,
	# 				"item_code": item.item_code,
	# 				"schedule_date": doctypelist.get_label("schedule_date",
	# 					parentfield="purchase_request_items"),
	# 				"posting_date": doctypelist.get_label("posting_date")
	# 			}, raise_exception=1)
	# 
	# def validate_qty_against_sales_order(self):
	# 	def _build_map():
	# 		"""build sales order item qty map"""
	# 		out_map = {}
	# 		for item in self.doclist.get({"parentfield": "purchase_request_items"}):
	# 			if item.sales_order:
	# 				out_map[item.sales_order][item.item_code] = \
	# 					out_map.setdefault(item.sales_order, {})\
	# 						.setdefault(item.item_code, 0) + \
	# 					flt(item.qty, self.precision.item.qty)
	# 		return out_map
	# 		
	# 	def _get_sales_order_items(sales_order):
	# 		return dict(webnotes.conn.sql("""select item_code,
	# 			sum(ifnull(qty, 0)) from `tabSales Order Item`
	# 			where parent=%s and docstatus=1 group by item_code""", (sales_order,)))
	# 	
	# 	for sales_order, item_qty_map in _build_map().items():
	# 		sales_order_items = _get_sales_order_items(sales_order)
	# 		
	# 		for item_code, qty in item_qty_map.items():
	# 			qty_already_requested = webnotes.conn.sql("""select sum(ifnull(qty, 0))
	# 				from `tabPurchase Request Item` where sales_order=%s and 
	# 				item_code=%s and docstatus=1 and parent!=%s""", 
	# 				(sales_order, item_code, self.doc.name))
	# 			qty_already_requested = qty_already_requested and \
	# 				flt(qty_already_requested[0][0], self.precision.item.qty) or 0
	# 			sales_order_item_qty = flt(sales_order_items.get(item_code),
	# 				self.precision.item.qty)
	# 
	# 			if (qty + qty_already_requested) > sales_order_item_qty:
	# 				item = self.doclist.getone({"parentfield": "purchase_request_items",
	# 					"item_code": item_code, "sales_order": sales_order})
	# 				
	# 				msgprint(_("""Row # %(idx)s, Item %(item_code)s: \
	# 					%(qty_label)s cannot be greater than %(diff)s, \
	# 					against Sales Order: \
	# 					<a href="#Form/Sales Order/%(sales_order)s">%(sales_order)s</a>.
	# 					Purchase Request has already been raised for \
	# 					%(qty_already_requested)s %(uom)s.
	# 					You can create an additional row to request more.""") % {
	# 						"idx": item.idx,
	# 						"item_code": item.item_code,
	# 						"qty_label": webnotes.get_label("Purchase Request", "qty",
	# 							parentfield="purchase_request_items"),
	# 						"diff": sales_order_item_qty - qty_already_requested,
	# 						"sales_order": sales_order,
	# 						"qty_already_requested": qty_already_requested,
	# 						"uom": item.uom,
	# 					}, raise_exception=1)
	# 					
	def validate_prevdoclist(self):
		from webnotes.model.mapper import validate_prev_doclist
		validate_prev_doclist("Purchase Request", "Supplier Quotation", self.doclist)
	
