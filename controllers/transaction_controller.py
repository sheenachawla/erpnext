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
from webnotes.utils import cint, formatdate, cstr, flt, add_days
from webnotes.model.code import get_obj
from webnotes.model.doc import make_autoname

import stock
from webnotes.model.controller import DocListController

class TransactionController(DocListController):
	def __init__(self, doc, doclist):
		super(TransactionController, self).__init__(doc, doclist)
		self.cur_docstatus = cint(webnotes.conn.get_value(self.doc.doctype, self.doc.name,
								"docstatus"))
		
	def autoname(self):
		self.doc.name = make_autoname(self.doc.naming_series+'.#####')
	
	def validate(self):
		self.validate_fiscal_year()
		self.validate_mandatory()
		self.validate_items()
		
		if self.doc.docstatus == 1 and self.cur_docstatus == 0:
			# a doc getting submitted should not be stopped
			self.doc.is_stopped = 0
	
	def on_update(self):
		pass
		
	def on_submit(self):
		pass
	
	def on_cancel(self):
		self.is_next_submitted()
	
	def load_precision_maps(self):
		if not hasattr(self, "precision"):
			from webnotes.model import doctype
			doctypelist = doctype.get(self.doc.doctype)
			self.precision = DictObj()
			self.precision.main = doctypelist.get_precision_map()
			self.precision.item = doctypelist.get_precision_map(parentfield = \
				self.item_table_field)
			if doctypelist.get_field("taxes_and_charges"):
				self.precision.tax = doctypelist.get_precision_map(parentfield = \
					"taxes_and_charges")
			
	def stop_resume_transaction(self):
		"""stop/resume a transaction if there is a change in is_stopped"""
		self.doc.is_stopped = cint(self.doc.is_stopped)
		is_stopped_old = webnotes.conn.get_value(self.doc.doctype, self.doc.name,
			"is_stopped")
		
		if self.doc.is_stopped != cint(is_stopped_old):
			self.update_bin()

			msgprint("%(doctype)s: %(name)s %(stopped)s." % {
				"doctype": _(self.doc.doctype),
				"name": self.doc.name,
				"stopped": self.doc.is_stopped and _("stopped") or _("resumed")
			})
			
	def validate_mandatory(self):
		if self.doc.amended_from and not self.doc.amendment_date:
			from webnotes.model import doctype
			msgprint(_("Please specify: %(label)s") % {"label":
				webnotes.model.doctype.get(self.doc.doctype).get_label("amendment_date")},
				raise_exception=1)
			
	def validate_fiscal_year(self):
		# TODO: fiscal_year field needs to be deprecated
		from accounts.utils import get_fiscal_year
		if get_fiscal_year(self.doc.posting_date)[0] != self.doc.fiscal_year:
			msgprint("""%(posting_date)s: not within Fiscal Year: %(fiscal_year)s""" % {
				"posting_date": formatdate(self.doc.posting_date),
				"fiscal_year": self.doc.fiscal_year
			})
			
	def validate_items(self):
		"""
			validate the following:
			* qty
			* is_stock_item
		"""
		import stock
		from webnotes.model.utils import validate_condition
		
		item_doclist = self.doclist.get({"parentfield": self.item_table_field})
		
		stock_items = []
		non_stock_items = []
		
		for item in item_doclist:
			# validate qty
			validate_condition(item, "qty", ">=", 0)
			
			item_controller = get_obj("Item", item.item_code)
			
			# validations for stock item
			self.validate_stock_item(item_controller.doc, item)
			
			# separate out stock and non-stop items for duplicate checking
			if item_controller.doc.is_stock_item == "Yes":
				stock_items.append(item_controller.doc.name)
			else:
				non_stock_items.append(item_controller.doc.name)
		
		self.check_duplicate(item_doclist, stock_items, non_stock_items)
		
		# to be overridden in each controller
		self.validate_prevdoclist()
		
	def validate_stock_item(self, item, child):
		stock.validate_end_of_life(item.name, item.end_of_life)
		
		# get warehouse field
		warehouse_field = webnotes.get_field(item.parenttype, "warehouse",
			parentfield=item.parentfield)
		
		if warehouse_field and item.is_stock_item == "Yes" and not child.warehouse:
			msgprint(_("""Row # %(idx)s, Item %(item_code)s: \
				Please specify Warehouse for Stock Item""") % \
				{"idx": child.idx, "item_code": item.name },
				raise_exception=1)
			
	def get_item_details(self, args):
		if isinstance(args, basestring):
			import json
			args = json.loads(args)

		args = DictObj(args)

		item = get_obj("Item", args.item_code, with_children=1)

		# validate end of life
		stock.validate_end_of_life(item.doc.item_code, item.doc.end_of_life)

		ret = DictObj({
			"item_name": cstr(item.doc.item_name),
			"item_group": cstr(item.doc.item_group),
			"brand": cstr(item.doc.brand),
			"description": cstr(item.doc.description),
			"uom": cstr(item.doc.stock_uom),
			"stock_uom": cstr(item.doc.stock_uom),
			"warehouse": args.warehouse or cstr(item.doc.default_warehouse),
			"conversion_factor": 1,
			"qty": 0,
			"discount": 0,
			"batch_no": "",
			"item_tax_rate": json.dumps(dict((item_tax.tax_type, item_tax.tax_rate)
				for item_tax in item.doclist.get({"parentfield": "item_tax"}))),
			"min_order_qty": flt(item.doc.min_order_qty,
				self.precision.item.min_order_qty),
		})

		if ret.warehouse:
			ret.projected_qty = stock.get_projected_qty(args.item_code,
				ret.warehouse)["projected_qty"]
		
		if self.doc.posting_date and item.doc.lead_time_days:
			ret.schedule_date = add_days(self.doc.posting_date, item.doc.lead_time_days)
			ret.leat_time_date = ret.schedule_date
			
		# TODO last purchase details for PO and Pur Receipt
		
		# TODO supplier part no for PO
		
		return ret
		
	def get_uom_details(self, args=None):
		"""get last purchase rate based on conversion factor"""
		# QUESTION why is this function called in purchase request?
		if not args:
			args = webnotes.form_dict.get("args")
			
		if isinstance(args, basestring):
			import json
			args = json.loads(args)
		
		args = DictObj(args)
		ret = DictObj()
		
		conversion_factor = flt(webnotes.conn.get_value("UOM Conversion Detail", 
			{"parent": args.item_code, "uom": args.uom}, "conversion_factor"))
		if not conversion_factor: return ret
		
		last_purchase_details = self.get_last_purchase_details(args.item_code,
			args.doc_name)
		exchange_rate = flt(args.exchange_rate, self.precision.main.exchange_rate)
		ref_rate = last_purchase_details.ref_rate * conversion_factor or 0
		rate = last_purchase_details.rate * conversion_factor or 0
		
		# TODO: check why stock_qty and not qty
		ret.update({
			"conversion_factor": conversion_factor,
			"qty": flt(flt(args.stock_qty, self.precision.item.stock_qty) / 
				conversion_factor, self.precision.item.qty),
			"ref_rate": ref_rate,
			"rate": rate,
			"print_ref_rate": ref_rate / exchange_rate,
			"print_rate": rate / exchange_rate,
		})
		
		return ret
		
	def get_tc_details(self):
		terms = webnotes.conn.get_value("Terms and Conditions", self.doc.tc_name,
			"terms")
		if terms:
			self.doc.terms = terms
	
	def is_next_submitted(self):
		from webnotes.model.mapper import is_next_submitted
		is_next_submitted(self.doc.doctype, self.doc.name)
	
	def append_taxes(self):
		"""append taxes as per tax master link field"""
		self.doclist = self.doclist.get({"parentfield": ["!=", "taxes_and_charges"]})
		
		doctypelist = webnotes.get_doctype(self.doc.doctype)
		tax_master_doctype = (doctypelist.get_options("taxes_and_charges_master"))\
			.split("\n")[0]
		tax_doctype = (doctypelist.get_options("taxes_and_charges")).split("\n")[0]
		
		master_tax_list = webnotes.get_doclist(tax_master_doctype,
			self.doc.taxes_and_charges_master).get({"parentfield": "taxes_and_charges"})
			
		for base_tax in master_tax_list:
			tax = DictObj([[field, base_tax.fields.get(field)]
				for field in base_tax.fields
				if field not in webnotes.model.default_fields])
			tax.update({
				"doctype": tax_doctype,
				"parentfield": "taxes_and_charges",
				"rate": flt(tax.rate, self.precision.tax.rate),
			})
			self.doclist.append(tax)