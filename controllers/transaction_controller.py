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
from webnotes import _, msgprint, DictObj

import webnotes.model
from webnotes.utils import cint, formatdate, cstr, flt, getdate
from webnotes.model.code import get_obj
from webnotes.model.doc import make_autoname

from webnotes.model.controller import DocListController
class TransactionController(DocListController):
	def autoname(self):
		self.doc.name = make_autoname(self.doc.naming_series+'.#####')
	
	def validate(self):
		self.validate_fiscal_year()
		
		# TODO
		# self.validate_mandatory()
		# self.validate_for_items()
		
	def on_cancel(self):
		# TODO
		# self.check_for_stopped_status
		# self.check_docstatus
		pass
	
	def load_precision_maps(self):
		if not hasattr(self, "precision"):
			from webnotes.model import doctype
			doctypelist = doctype.get(self.doc.doctype)
			self.precision = DictObj()
			self.precision.main = doctypelist.get_precision_map()
			self.precision.item = doctypelist.get_precision_map(parentfield = \
				self.item_table_field)
			if hasattr(self, "tax_table_field"):
				self.precision.tax = doctypelist.get_precision_map(parentfield = \
					self.tax_table_field)
			
	def set_schedule_date(self, item_table_field=None):
		"""set schedule date in items as posting_date + lead_time_days"""
		prevdoc_fields = webnotes.model.get_prevdoc_fields(self.doc.doctype)
		
		if not item_table_field:
			item_table_field = webnotes.form_dict.get("item_table_field") or \
				self.item_table_field
		
		for d in self.doclist.get({"parenfield": item_table_field}):
			lead_time_days = webnotes.conn.sql("""select ifnull(lead_time_days, 0)
				from `tabItem` where name=%s and (ifnull(end_of_life, "")="" 
				or end_of_life="0000-00-00" or end_of_life > now())""", (d.item_code,))
			lead_time_days = lead_time_days and cint(lead_time_days[0][0]) or 0

			if lead_time_days:
				d.lead_time_date = add_days(self.doc.posting_date, lead_time_days)
				if not any([d.fields.get(f) for f in prevdoc_fields]):
					# i.e. if not mapped using doctype mapper
					d.schedule_date = add_days(self.doc.posting_date, lead_time_days)
	
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
			
	def validate_fiscal_year(self):
		# TODO: fiscal_year field needs to be deprecated
		from accounts.utils import get_fiscal_year
		if get_fiscal_year(self.doc.posting_date)[0] != self.doc.fiscal_year:
			msgprint("""%(posting_date)s: not within Fiscal Year: %(fiscal_year)s""" % {
				"posting_date": formatdate(self.doc.posting_date),
				"fiscal_year": self.doc.fiscal_year
			})
			
	def validate_mandatory(self):
		if self.doc.amended_from and not self.doc.amendment_date:
			from webnotes.model import doctype
			msgprint(_("Please specify: %(label)s") % { "label":
				doctype.get(self.doc.doctype).get_label("amendment_date") },
				raise_exception=1)
		
	def validate_items(self):
		"""
			validate the following:
			* qty
			* is_stock_item
			*
		"""
		from webnotes.model.utils import check_duplicate, validate
		
		item_doclist = self.doclist.get({"parentfield": self.item_table_field})
		
		stock_items = []
		non_stock_items = []
		
		for item in item_doclist:
			# validate qty
			validate(item, "qty", ">=", 0)
			
			# TODO update redundancies
			
			item_obj = get_obj("Item", item.item_code)
			self.validate_stock_item(item_obj, item)
			
			# TODO validate with prevdoc
			
			if item_obj.doc.is_stock_item == "Yes":
				stock_items.append(item_obj.doc.name)
			else:
				non_stock_items.append(item_obj.doc.name)
		
		# duplicate checking for stock items
		prevdoc_fields = webnotes.model.get_prevdoc_fields(self.doc.doctype)
		prevdoc_detail_fields = [(f + "_item") for f in prevdoc_fields]
		check_duplicate(item_doclist.get({"item_code": ["in", stock_items]})),
			["schedule_date", "item_code", "description", "warehouse", "batch_no"] + \
			prevdoc_fields + prevdoc_detail_fields)
		
		# duplicate checking for non-stock items
		check_duplicate(item_doclist.get({"item_code": ["in", non_stock_items]}),
			["schedule_date", "item_code", "description"])
			
	def validate_stock_item(self, item_obj, child_doc):
		item = item_obj.doc
		
		import stock
		stock.validate_end_of_life(item.name, item.end_of_life)
		
		msg = _("Row # %(idx)s, Item %(item_code)s: ")
		if item.is_stock_item == "Yes" and not child_doc.warehouse:
			msgprint((msg + _("""Please specify Warehouse for Stock Item""")) % \
			{"idx": child.idx, "item_code": item.name}, raise_exception=1)
		
		if item.is_purchase_item != "Yes" and item.is_subcontracted_item != "Yes":
			msgprint((msg + _("""Not a Purchase / Sub-contracted Item""")),
			raise_exception=1)
		
	def get_item_details(self, args=None):
		if not args:
			args = webnotes.form_dict.get("args")

		if isinstance(args, basestring):
			import json
			args = json.loads(args)

		args = DictObj(args)

		item = get_obj("Item", args.item_code, with_children=1)

		# validate end of life
		import stock
		import sys
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
		
	def get_last_purchase_details(self, item_code, doc_name):
		query = """select parent.name, parent.posting_date, item.conversion_factor,
			item.ref_rate, item.discount, item.rate %s
			from `tab%s` parent, `tab%s` item
			where parent.name = item.parent and item.item_code = %s 
			and parent.docstatus = 1 and parent.name != %s
			order by parent.posting_date desc, %s parent.name desc limit 1"""
			
		last_purchase_order_item = webnotes.conn.sql(query % \
			("Purchase Order", "Purchase Order Item", "%s", "%s", ""),
			(item_code, doc_name), as_dict=1)
		
		last_purchase_receipt_item = webnotes.conn.sql(query % \
			("Purchase Receipt", "Purchase Receipt Item", "%s", "%s",
			"parent.posting_time desc, "), (item_code, doc_name), as_dict=1)
		
		# get the last purchased item, by comparing dates	
		if last_purchase_order_item and last_purchase_receipt_item:
			purchase_order_date = getdate(last_purchase_order_item[0].posting_date)
			purchase_receipt_date = getdate(last_purchase_receipt_item[0].posting_date)
			if purchase_order_date > purchase_receipt_date:
				last_purchase_item = last_purchase_order_item[0]
			else:
				last_purchase_item = last_purchase_receipt_item[0]
		elif last_purchase_order_item:
			last_purchase_item = last_purchase_order_item[0]
		elif last_purchase_receipt_item:
			last_purchase_item = last_purchase_receipt_item[0]
		else:
			# if none exists
			return DictObj(), getdate("2000-01-01")
		
		last_purchase_date = getdate(last_purchase_item.posting_date)
		conversion_factor = flt(last_purchase_item.conversion_factor)
		
		# prepare last purchase details, dividing by conversion factor
		last_purchase_details = DictObj({
			"ref_rate": flt((last_purchase_item.ref_rate / conversion_factor),
				self.precision.item.ref_rate),
			"rate": flt((last_purchase_item.rate / conversion_factor),
				self.precision.item.rate),
			"discount": flt(last_purchase_item.discount, self.precision.item.discount),
			"last_purchase_date": last_purchase_date
		})
		
		return last_purchase_details
			
	def get_tc_details(self):
		terms = webnotes.conn.get_value("Terms and Conditions", self.doc.tc_name,
			"terms")
		if terms:
			self.doc.terms = terms