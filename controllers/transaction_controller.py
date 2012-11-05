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
from webnotes.model.controller import get_obj
from webnotes.model.doc import make_autoname, Document

import stock
from webnotes.model.controller import DocListController

class TransactionController(DocListController):
	def __init__(self, doc, doclist):
		super(TransactionController, self).__init__(doc, doclist)
		self.cur_docstatus = cint(webnotes.conn.get_value(self.doc.doctype, 
			self.doc.name, "docstatus"))
		
	def autoname(self):
		self.doc.name = make_autoname(self.doc.naming_series+'.#####')
	
	def validate(self):
		self.validate_fiscal_year()
		self.validate_mandatory()
		self.validate_items()
		if self.doc.docstatus == 1 and self.cur_docstatus == 0:
			# a doc getting submitted should not be stopped
			self.doc.is_stopped = 0
			
	def on_map(self):
		self.set_item_values()
		self.append_default_taxes()

	def set_item_values(self):
		for item in self.doclist.get({"parentfield": self.item_table_field}):
			item_values = self.get_item_details({"item_code": item.item_code})
			for k in item_values:
				if not item.fields.get(k):
					item.fields[k] = item_values[k]
	
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
			* qty >= 0
			* stock item
			* duplicate rows
			* mapping with previous doclist
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
			"item_name": item.doc.item_name,
			"item_group": item.doc.item_group,
			"brand": item.doc.brand,
			"description": item.doc.description,
			"uom": item.doc.stock_uom,
			"stock_uom": item.doc.stock_uom,
			"warehouse": args.warehouse or item.doc.default_warehouse,
			"conversion_factor": 1,
			"qty": 0,
			"discount": 0,
			"batch_no": "",
			"item_tax_rate": json.dumps(dict((item_tax.tax_type, item_tax.tax_rate)
				for item_tax in item.doclist.get({"parentfield": "item_tax"}))),
			"min_order_qty": flt(item.doc.min_order_qty, 
				self.precision.item.min_order_qty),
			"income_account": item.doc.default_income_account or args.income_account,
			"cost_center": item.doc.default_sales_cost_center or args.cost_center,
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
			
	def get_address(self, args):
		args = DictObj(args)
		address_field = self.meta.get_field({"options": "^Address"})
		
		query = "select * from `tabAddress` where docstatus < 2 "
		
		if args.customer:
			query += "and customer=%s order by "
			if args.is_shipping_address:
				query += "is_shipping_address desc, "
			query += "is_primary_address desc limit 1"
			val = args.customer
		elif args.supplier:
			query += "and supplier=%s order by "
			if args.is_shipping_address:
				query += "is_shipping_address desc, "
			query += "is_primary_address desc limit 1"
			val = args.supplier
		else:
			query += "and name=%s"
			val = self.doc.fields.get(address_field)
		
		address_result = webnotes.conn.sql(query, (val,), as_dict=1)
		
		if address_result:
			address_doc = Document("Address", fielddata=address_result[0])
			
			self.doc.fields[address_field] = address_doc.name
			
			self.doc.address_display = "\n".join(filter(None, [
				address_doc.address_line1,
				address_doc.address_line2,
				" ".join(filter(None, [address_doc.city, address_doc.pincode])),
				address_doc.state,
				address_doc.country,
				address_doc.phone and ("Phone: %s" % address_doc.phone) or "",
				address_doc.fax and ("Fax: %s" % address_doc.fax) or "",
			]))
			
			# send it on client side - can be used for further processing
			webnotes.response.setdefault("docs", []).append(address_doc)

	def get_contact(self, args):
		args = DictObj(args)
		contact_field = self.meta.get_field({"options": "^Contact"})

		query = "select * from `tabContact` where docstatus < 2 "
		
		if args.customer:
			query += "and customer=%s order by is_primary_contact desc limit 1"
			val = args.customer
		elif args.supplier:
			query += "and supplier=%s order by is_primary_contact desc limit 1"
			val = args.supplier
		else:
			query += "and name=%s"
			val = self.doc.fields.get(contact_field)
			
		contact_result = webnotes.conn.sql(query, (val,), as_dict=1)
		
		if contact_result:
			contact_doc = Document("Contact", fielddata=contact_result[0])
			
			self.doc.fields[contact_field] = contact_doc.name
			
			self.doc.contact_display = " ".join(filter(None, 
				[contact_doc.first_name, contact_doc.last_name]))
			
			self.doc.contact_person = contact_doc.name
			self.doc.contact_email = contact_doc.email_id
			self.doc.contact_mobile = contact_doc.mobile_no
			self.doc.contact_designation = contact_doc.designation
			self.doc.contact_department = contact_doc.department
			
			# send it on client side - can be used for further processing
			webnotes.response.setdefault("docs", []).append(contact_doc)
			
	def calculate_taxes_and_totals(self):
		"""
			Calculates:
				* amount for each item
				* item_tax_amount for each item, 
				* tax amount and tax total for each tax
				* net total
				* total taxes
				* grand total
		"""
		self.prepare_precision_maps()
		self.item_doclist = self.doclist.get({"parentfield": self.fname})
		self.tax_doclist = self.doclist.get({"parentfield": self.taxes_and_charges})

		self.calculate_net_total()
		self.initialize_taxes()
			
		self.calculate_taxes()
		self.calculate_totals()
			
	def calculate_net_total(self):
		self.doc.net_total = 0
		for item in self.item_doclist:
			# round relevant values
			round_doc(item, self.item_precision)
			
			# calculate amount and net total
			item.amount = flt((item.qty * item.rate) - \
				((flt(item.discount, self.item_precision["amount"]) / 100.0) * item.rate), 
				self.item_precision["amount"])
			self.doc.net_total += item.amount
			
		self.doc.net_total = flt(self.doc.net_total, self.main_precision["net_total"])
		
	def initialize_taxes(self):
		for tax in self.tax_doclist:
			# initialize totals to 0
			tax.tax_amount = tax.total = 0
			tax.grand_total_for_current_item = tax.tax_amount_for_current_item = 0
			tax.item_wise_tax_detail = {}
			
			# round relevant values
			round_doc(tax, self.tax_precision)
			
	def calculate_taxes(self):
		def _load_item_tax_rate(item_tax_rate):
			if not item_tax_rate:
				return {}

			return json.loads(item_tax_rate)

		def _get_tax_rate(item_tax_map, tax):
			if item_tax_map.has_key(tax.account_head):
				return flt(item_tax_map.get(tax.account_head), self.tax_precision["rate"])
			else:
				return tax.rate
		
		def _get_current_tax_amount(item, tax, item_tax_map):
			tax_rate = _get_tax_rate(item_tax_map, tax)
	
			if tax.charge_type == "Actual":
				# distribute the tax amount proportionally to each item row
				current_tax_amount = (self.doc.net_total
					and ((item.amount / self.doc.net_total) * tax.rate)
					or 0)
			elif tax.charge_type == "On Net Total":
				current_tax_amount = (tax_rate / 100.0) * item.amount
			elif tax.charge_type == "On Previous Row Amount":
				current_tax_amount = (tax_rate / 100.0) * \
					self.tax_doclist[cint(tax.row_id) - 1].tax_amount_for_current_item
			elif tax.charge_type == "On Previous Row Total":
				current_tax_amount = (tax_rate / 100.0) * \
					self.tax_doclist[cint(tax.row_id) - 1].grand_total_for_current_item
	
			return flt(current_tax_amount, self.tax_precision["tax_amount"])
		
		# build is_stock_item_map
		item_codes = list(set(item.item_code for item in self.item_doclist))
		is_stock_item_map = dict(webnotes.conn.sql("""select name, 
			ifnull(is_stock_item, "No") from `tabItem` where name in (%s)""" % \
			(", ".join((["%s"]*len(item_codes))),),
			item_codes))
		
		# loop through items and set item tax amount
		for item in self.item_doclist:
			item_tax_map = _load_item_tax_rate(item.item_tax_rate)
			item.item_tax_amount = 0
			
			for i, tax in enumerate(self.tax_doclist):
				# tax_amount represents the amount of tax for the current step
				current_tax_amount = _get_current_tax_amount(item, tax, item_tax_map)
				
				if self.transaction_type == "Purchase" and \
						tax.category in ["Valuation", "Valuation and Total"] and \
						is_stock_item_map.get(item.item_code)=="Yes":
					item.item_tax_amount += current_tax_amount
				
				# case when net total is 0 but there is an actual type charge
				# in this case add the actual amount to tax.tax_amount
				# and tax.grand_total_for_current_item for the first such iteration
				zero_net_total_adjustment = 0
				if not (current_tax_amount or self.doc.net_total or tax.tax_amount) and \
						tax.charge_type=="Actual":
					zero_net_total_adjustment = flt(tax.rate, self.tax_precision["tax_amount"])
				
				# store tax_amount for current item as it will be used for
				# charge type = 'On Previous Row Amount'
				tax.tax_amount_for_current_item = current_tax_amount + \
					zero_net_total_adjustment
				
				# accumulate tax amount into tax.tax_amount
				tax.tax_amount += tax.tax_amount_for_current_item
				
				if self.transaction_type == "Purchase" and tax.category == "Valuation":
					# if just for valuation, do not add the tax amount in total
					# hence, setting it as 0 for further steps
					current_tax_amount = zero_net_total_adjustment = 0
				
				# Calculate tax.total viz. grand total till that step
				# note: grand_total_for_current_item contains the contribution of 
				# item's amount, previously applied tax and the current tax on that item
				if i==0:
					tax.grand_total_for_current_item = flt(item.amount +
						current_tax_amount + zero_net_total_adjustment, 
						self.tax_precision["total"])
				else:
					tax.grand_total_for_current_item = \
						flt(self.tax_doclist[i-1].grand_total_for_current_item +
							current_tax_amount + zero_net_total_adjustment,
							self.tax_precision["total"])
				
				# prepare itemwise tax detail
				tax.item_wise_tax_detail[item.item_code] = current_tax_amount
				
				# in tax.total, accumulate grand total of each item
				tax.total += tax.grand_total_for_current_item
		
		# QUESTION: is this necessary?
		# store itemwise tax details as a json
		for tax in self.tax_doclist:
			tax.item_wise_tax_detail = json.dumps(tax.item_wise_tax_detail)
			# print tax.item_wise_tax_detail
				
	def calculate_totals(self):
		if self.tax_doclist:
			self.doc.grand_total = self.tax_doclist[-1].total
		else:
			self.doc.grand_total = self.doc.net_total
		
		self.doc.grand_total = flt(self.doc.grand_total,
			self.main_precision["grand_total"])
		
		self.doc.fields[self.taxes_and_charges_total] = \
			flt(self.doc.grand_total - self.doc.net_total,
			self.main_precision[self.taxes_and_charges_total])
		
		self.set_amount_in_words()
		
		# self.doc.rounded_total = round(self.doc.grand_total)
		
		# TODO: calculate import / export values
		
	def set_amount_in_words(self):
		from webnotes.utils import money_in_words
		default_currency = webnotes.conn.get_value("Company", self.doc.company, "default_currency")
		
		self.doc.grand_total_in_words = money_in_words(self.doc.grand_total, default_currency)
		self.doc.rounded_total_in_words = money_in_words(self.doc.rounded_total, default_currency)
		
		self.doc.grand_total_in_words_print = \
			money_in_words(self.doc.grand_total_print, default_currency)
		self.doc.rounded_total_in_words_print = \
			money_in_words(self.doc.rounded_total_print, default_currency)
			
	def prepare_precision_maps(self):
		doctypelist = webnotes.model.doctype.get(self.doc.doctype)
		self.main_precision = doctypelist.get_precision_map()
		self.item_precision = doctypelist.get_precision_map(parentfield=self.fname)
		self.tax_precision = \
			doctypelist.get_precision_map(parentfield=self.taxes_and_charges)
