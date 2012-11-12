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
from webnotes.model.utils import round_doc
import json

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
		
		if self.doc.docstatus == 1:
			self.stop_resume_transaction()
			
		if self.meta.get_field("taxes_and_charges"):
			self.calculate_taxes_and_totals()
			
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
	
	@property
	def precision(self):
		if not hasattr(self, "_precision"):
			self._precision = DictObj()
			self._precision.main = self.meta.get_precision_map()
			self._precision.item = self.meta.get_precision_map(parentfield = \
				self.item_table_field)
			if self.meta.get_field("taxes_and_charges"):
				self._precision.tax = self.meta.get_precision_map(parentfield = \
					"taxes_and_charges")
					
		return self._precision
	
	def stop_resume_transaction(self):
		"""stop/resume a transaction if there is a change in is_stopped"""
		self.doc.is_stopped = cint(self.doc.is_stopped)
		is_stopped_old = webnotes.conn.get_value(self.doc.doctype, self.doc.name,
			"is_stopped")
		
		if self.doc.is_stopped != cint(is_stopped_old):
			# TODO deprecate bin
			self.update_bin()

			msgprint("%(doctype)s: %(name)s %(stopped)s." % {
				"doctype": _(self.doc.doctype),
				"name": self.doc.name,
				"stopped": self.doc.is_stopped and _("stopped") or _("resumed")
			})
			
	def validate_mandatory(self):
		if self.doc.amended_from and not self.doc.amendment_date:
			msgprint(_("Please specify") + ": %(label)s" % \
				{"label": self.meta.get_label("amendment_date")}, raise_exception=1)
			
	def validate_fiscal_year(self):
		# TODO: fiscal_year field needs to be deprecated
		from accounts.utils import get_fiscal_year
		if get_fiscal_year(self.doc.posting_date)[0] != self.doc.fiscal_year:
			msgprint("%(posting_date)s: " + _("not within Fiscal Year") + \
				": %(fiscal_year)s" % {
					"posting_date": formatdate(self.doc.posting_date),
					"fiscal_year": self.doc.fiscal_year
				}, raise_exception=1)
			
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
		warehouse_field = webnotes.get_field(child.parenttype, "warehouse",
			parentfield=child.parentfield)
		
		if warehouse_field and item.is_stock_item == "Yes" and not child.warehouse:
			msgprint((_("Row") + " # %(idx)s, " + _("Item") + " %(item_code)s: " + \
				_("Please specify Warehouse for Stock Item")) % \
				{"idx": child.idx, "item_code": item.name },
				raise_exception=1)
			
	def get_item_details(self, args, item=None):
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
			"amount": 0,
			"print_amount": 0,
			"serial_no": "",
			"batch_no": "",
			"item_tax_rate": json.dumps(dict((item_tax.tax_type, item_tax.tax_rate)
				for item_tax in item.doclist.get({"parentfield": "item_tax"}))),
		})
		
		return ret
		
	def process_args(self, args, item=None):
		if isinstance(args, basestring):
			args = json.loads(args)

		args = DictObj(args)

		if not item:
			item = get_obj("Item", args.item_code, with_children=1)

		return args, item
	
	@property
	def stock_items(self):
		if not hasattr(self, "_stock_items"):
			if not self.item_doclist:
				self.item_doclist = self.doclist.get({"parentfield": self.item_table_field})
			
			item_codes = list(set(item.item_code for item in self.item_doclist))
			self._stock_items = [r[0] for r in webnotes.conn.sql("""select name
				from `tabItem` where name in (%s) and is_stock_item='Yes'""" % \
				(", ".join((["%s"]*len(item_codes))),), item_codes)]

		return self._stock_items
		
	def get_barcode_details(self, args):
		item = self.get_item_code(args["barcode"])
		ret = args.update({'item_code': item})
		if item:
			ret = self.get_item_details(ret)
			
		return ret
		
	def get_item_code(self, barcode):
		item = webnotes.conn.sql("""select name, end_of_life, is_sales_item, is_service_item 
			from `tabItem` where barcode = %s""", barcode, as_dict=1)
			
		if not item:
			msgprint(_("No item found for this barcode") + ": " + barcode + ". " + 
				_("May be barcode not updated in item master. Please check"))

		elif item[0]['end_of_life'] and getdate(cstr(item[0]['end_of_life'])) < nowdate():
			msgprint(_("Item") + ": " + item[0]['name'] + _(" has been expired.") +  
				_("Please check 'End of Life' field in item master"))

		elif item[0]['is_sales_item'] == 'No' and item[0]['is_service_item'] == 'No':
			msgprint(_("Item") + ": "+ item[0]['name'] +_(" is not a sales or service item"))

		elif len(item) > 1:
			msgprint(_("""There are multiple item for this barcode. 
				Please select item code manually"""))
		else:
			return item[0]["name"]
	
	def get_uom_details(self, args=None):
		"""get last purchase rate based on conversion factor"""
		# QUESTION why is this function called in purchase request?
		if not args:
			args = webnotes.form_dict.get("args")
			
		if isinstance(args, basestring):
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
			
	def set_address(self, args):
		address = self.get_address(args)
		if args.get("is_shipping_address"):
			self.doc.shipping_address_name = address["name"]
			self.doc.shipping_address = address["address_display"]
		else:
			self.doc.customer_address = address["name"]
			self.doc.address_display = address["address_display"]
			
	def get_address(self, args):
		args = DictObj(args)
		
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
			val = args.name
		
		address_result = webnotes.conn.sql(query, (val,), as_dict=1)
		
		if address_result:
			address_doc = Document("Address", fielddata=address_result[0])
						
			address_display = "\n".join(filter(None, [
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
			
			return {
				"name": address_doc.name, 
				"address_display": address_display
			}

	def set_contact(self, args):
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
			
			self.doc.fields[contact_field.fieldname] = contact_doc.name
			
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
				* valuation_tax_amount for each item, 
				* tax amount and tax total for each tax
				* net total
				* total taxes
				* grand total
		"""
		self.item_doclist = self.doclist.get({"parentfield": self.item_table_field})
		self.tax_doclist = self.doclist.get({"parentfield": "taxes_and_charges"})

		self.calculate_item_values()
		
		self.initialize_taxes()
		if self.meta.get_field("included_in_print_rate", parentfield="taxes_and_charges"):
			self.determine_exclusive_rate()
		
		self.calculate_net_total()
		self.calculate_taxes()
		self.calculate_totals()
		self.set_amount_in_words()
		
	def calculate_item_values(self):
		self.doc.exchange_rate = flt(self.doc.exchange_rate,
			self.precision.main.exchange_rate)
			
		def _set_base(item, from_field, to_field):
			item.fields[to_field] = flt(
				(flt(item.fields[from_field], self.precision.item[from_field]) * 
					self.doc.exchange_rate),
				self.precision.item[to_field])
		
		for item in self.item_doclist:
			round_doc(item, self.precision.item)
			
			if item.discount == 100:
				if not item.print_ref_rate:
					item.print_ref_rate = item.print_rate
				item.print_rate = 0
			else:
				if item.print_ref_rate:
					item.print_rate = flt(item.print_ref_rate *
						(1.0 - (item.discount / 100.0)),
						self.precision.item.print_rate)
				else:
					# assume that print rate and discount are specified
					item.print_ref_rate = flt(item.print_rate / 
						(1.0 - (item.discount / 100.0)),
						self.precision.item.print_ref_rate)
						
			item.print_amount = flt(item.print_rate * item.qty,
				self.precision.item.print_amount)
				
			_set_base(item, "print_ref_rate", "ref_rate")
			_set_base(item, "print_rate", "rate")
			_set_base(item, "print_amount", "amount")
			
	def calculate_net_total(self):
		self.doc.net_total = 0
		self.doc.net_total_print = 0
		
		for item in self.item_doclist:
			self.doc.net_total += item.amount
			self.doc.net_total_print += item.print_amount

		self.doc.net_total = flt(self.doc.net_total, self.precision.main.net_total)
		self.doc.net_total_print = flt(self.doc.net_total_print,
			self.precision.main.net_total_print)
		
	def initialize_taxes(self):
		for tax in self.tax_doclist:
			# initialize totals to 0
			tax.tax_amount = tax.total = tax.tax_amount_print = tax.total_print = 0
			tax.grand_total_for_current_item = tax.tax_amount_for_current_item = 0
			
			if tax.charge_type in ["On Previous Row Amount", "On Previous Row Total"]:
				self.validate_on_previous_row(tax)
			
			# round relevant values
			round_doc(tax, self.precision.tax)
			
	def validate_on_previous_row(self, tax):
		"""
			validate if a valid row id is mentioned in case of
			On Previous Row Amount and On Previous Row Total
		"""
		if not tax.row_id or tax.row_id >= tax.idx:
			msgprint((_("Row") + " # %(idx)s [%(taxes_doctype)s]: " + \
				_("Please specify a valid") + " %(row_id_label)s") % {
					"idx": tax.idx,
					"taxes_doctype": self.meta.get_options("taxes_and_charges"),
					"row_id_label": self.meta.get_label("row_id",
						parentfield="taxes_and_charges")
				}, raise_exception=True)
				
		if cint(tax.included_in_print_rate):
			if tax.charge_type == "Actual":
				# now inclusive rate for type 'Actual'
				msgprint((_("Row") + " # %(idx)s [%(taxes_doctype)s]: " + \
					"'%(charge_type_label)s' = '%(charge_type)s' " + \
					_("cannot be included in item's rate")) % {
						"idx": tax.idx,
						"taxes_doctype": self.meta.get_options("taxes_and_charges"),
						"charge_type_label": self.meta.get_label("charge_type",
							parentfield="taxes_and_charges"),
						"charge_type": tax.charge_type,
					}, raise_exception=True)
			
			elif tax.charge_type == "On Previous Row Total" and \
					not all([cint(t.included_in_print_rate) \
						for t in self.tax_doclist[:tax.idx - 1]]):
				# for an inclusive tax of type "On Previous Row Total", 
				# all rows above it should also be inclusive
				msgprint((_("Row") + " # %(idx)s [%(taxes_doctype)s]: " + \
					_("If") + " '%(inclusive_label)s' " + _("is checked for") + \
					" '%(charge_type_label)s' = '%(charge_type)s', " + _("then") + " " + \
					_("Row") + " # %(row_range)s " + _("should also have") + \
					" '%(inclusive_label)s' = " + _("checked")) % {
						"idx": tax.idx,
						"taxes_doctype": self.meta.get_options("taxes_and_charges"),
						"inclusive_label": self.meta.get_label("included_in_print_rate",
							parentfield="taxes_and_charges"),
						"charge_type_label": self.meta.get_label("charge_type",
							parentfield="taxes_and_charges"),
						"charge_type": tax.charge_type,
						"row_range": "1 - %d" % (tax.idx - 1),
					}, raise_exception=True)
		
	def _load_item_tax_rate(self, item_tax_rate):
		if not item_tax_rate:
			return {}

		return json.loads(item_tax_rate)
		
	def _get_tax_rate(self, tax, item_tax_map):
		if item_tax_map.has_key(tax.account_head):
			return flt(item_tax_map.get(tax.account_head), self.precision.tax.rate)
		else:
			return tax.rate
			
	def calculate_taxes(self):
		# loop through items and set item tax amount
		for item in self.item_doclist:
			item_tax_map = self._load_item_tax_rate(item.item_tax_rate)
			item.valuation_tax_amount = 0
			
			for i, tax in enumerate(self.tax_doclist):
				# tax_amount represents the amount of tax for the current step
				current_tax_amount = self.get_current_tax_amount(item, tax, item_tax_map)
				
				if hasattr(self, "set_valuation_tax_amount"):
					self.set_valuation_tax_amount(item, tax, current_tax_amount)
				
				# case when net total is 0 but there is an actual type charge
				# in this case add the actual amount to tax.tax_amount
				# and tax.grand_total_for_current_item for the first such iteration
				zero_net_total_adjustment = 0
				if not (current_tax_amount or self.doc.net_total or tax.tax_amount) and \
						tax.charge_type=="Actual":
					zero_net_total_adjustment = flt(tax.rate,
						self.precision.tax.tax_amount)
				
				# store tax_amount for current item as it will be used for
				# charge type = 'On Previous Row Amount'
				tax.tax_amount_for_current_item = current_tax_amount + \
					zero_net_total_adjustment
				
				# accumulate tax amount into tax.tax_amount
				tax.tax_amount += tax.tax_amount_for_current_item
				if not cint(tax.included_in_print_rate):
					tax.tax_amount_print += flt(tax.tax_amount_for_current_item /
						self.doc.exchange_rate, self.precision.tax.tax_amount_print)
				
				if tax.category == "Valuation":
					# if just for valuation, do not add the tax amount in total
					# hence, setting it as 0 for further steps
					current_tax_amount = zero_net_total_adjustment = 0
				
				# Calculate tax.total viz. grand total till that step
				# note: grand_total_for_current_item contains the contribution of 
				# item's amount, previously applied tax and the current tax on that item
				if i==0:
					tax.grand_total_for_current_item = flt(item.amount +
						current_tax_amount + zero_net_total_adjustment, 
						self.precision.tax.total)
					
					# inclusive pricing complication
					if cint(tax.included_in_print_rate):
						tax.grand_total_print_for_current_item = flt(item.print_amount,
							self.precision.tax.total_print)
					else:
						tax.grand_total_print_for_current_item = flt(item.print_amount +
							((current_tax_amount + zero_net_total_adjustment) / 
							self.doc.exchange_rate), self.precision.tax.total_print)
				else:
					tax.grand_total_for_current_item = \
						flt(self.tax_doclist[i-1].grand_total_for_current_item +
							current_tax_amount + zero_net_total_adjustment,
							self.precision.tax.total)
					
					# inclusive pricing complication
					if cint(tax.included_in_print_rate):
						tax.grand_total_print_for_current_item = \
							self.tax_doclist[i-1].grand_total_print_for_current_item
					else:
						tax.grand_total_print_for_current_item = \
							flt(self.tax_doclist[i-1].grand_total_print_for_current_item +
								((current_tax_amount + zero_net_total_adjustment) / 
								self.doc.exchange_rate), self.precision.tax.total_print)
				
				# in tax.total, accumulate grand total of each item
				tax.total += tax.grand_total_for_current_item
				tax.total_print += tax.grand_total_print_for_current_item
				
				# TODO store tax_breakup for each item
	
	def get_current_tax_amount(self, item, tax, item_tax_map):
		tax_rate = self._get_tax_rate(tax, item_tax_map)

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

		return flt(current_tax_amount, self.precision.tax["tax_amount"])
		
	def calculate_totals(self):
		"""calculate total for accounting (base currency)"""
		if self.tax_doclist:
			self.doc.grand_total = self.tax_doclist[-1].total
			self.doc.grand_total_print = self.tax_doclist[-1].total_print
		else:
			self.doc.grand_total = self.doc.net_total
			self.doc.grand_total_print = self.doc.net_total_print
		
		self.doc.grand_total = flt(self.doc.grand_total,
			self.precision.main.grand_total)
		self.doc.grand_total_print = flt(self.doc.grand_total_print,
			self.precision.main.grand_total_print)
			
		self.doc.taxes_and_charges_total = \
			flt(self.doc.grand_total - self.doc.net_total,
			self.precision.main.taxes_and_charges_total)
			
		self.doc.taxes_and_charges_total_print = \
			flt(self.doc.grand_total_print - self.doc.net_total_print,
			self.precision.main.taxes_and_charges_total_print)
		
		self.doc.rounded_total = round(self.doc.grand_total)
		self.doc.rounded_total_print = round(self.doc.grand_total_print)
		
	def set_amount_in_words(self):
		from webnotes.utils import money_in_words
		default_currency = webnotes.conn.get_value("Company", self.doc.company, "default_currency")
		
		self.doc.grand_total_in_words = money_in_words(self.doc.grand_total,
			default_currency)
		self.doc.rounded_total_in_words = money_in_words(self.doc.rounded_total,
			default_currency)
		
		self.doc.grand_total_in_words_print = \
			money_in_words(self.doc.grand_total_print, default_currency)
		self.doc.rounded_total_in_words_print = \
			money_in_words(self.doc.rounded_total_print, default_currency)
			
	def determine_exclusive_rate(self):
		if not any((cint(tax.included_in_print_rate) for tax in self.tax_doclist)):
			# if no tax is marked as included in print rate, no need to proceed further
			return
			
		for item in self.item_doclist:
			item_tax_map = self._load_item_tax_rate(item.item_tax_rate)
			
			cumulated_tax_fraction = 0
			
			for i, tax in enumerate(self.tax_doclist):
				if cint(tax.included_in_print_rate):
					tax.tax_fraction_for_current_item = \
						self.get_current_tax_fraction(tax, item_tax_map)
					# tax.tax_fraction_for_current_item = \
					# 	flt(self.get_current_tax_fraction(tax, item_tax_map),
					# 		self.precision.tax.rate)
				else:
					tax.tax_fraction_for_current_item = 0
				
				if i==0:
					tax.grand_total_fraction_for_current_item = 1 + \
						tax.tax_fraction_for_current_item
				else:
					tax.grand_total_fraction_for_current_item = \
						self.tax_doclist[i-1].grand_total_fraction_for_current_item \
						+ tax.tax_fraction_for_current_item
						
				cumulated_tax_fraction += tax.tax_fraction_for_current_item
			
			if cumulated_tax_fraction:
				# item.amount = flt((item.print_amount * self.doc.exchange_rate) /
				# 	(1 + cumulated_tax_fraction), self.precision.item.amount)
				# 
				# item.rate = flt(item.amount / item.qty, self.precision.item.rate)
				
				item.rate = flt((item.print_rate * self.doc.exchange_rate) / 
					(1 + cumulated_tax_fraction), self.precision.item.rate)
				
				item.amount = flt(item.rate * item.qty, self.precision.item.amount)
				
				item.ref_rate = flt(item.rate / (1 - (item.discount / 100.0)),
					self.precision.item.ref_rate)
		
				print item.print_rate, 1+cumulated_tax_fraction, item.rate, item.amount
				print "-"*10

	def get_current_tax_fraction(self, tax, item_tax_map):
		"""
			Get tax fraction for calculating tax exclusive amount
			from tax inclusive amount
		"""
		current_tax_fraction = 0
		
		if cint(tax.included_in_print_rate):
			tax_rate = self._get_tax_rate(tax, item_tax_map)
			
			if tax.charge_type == "On Net Total":
				current_tax_fraction = tax_rate / 100.0
			
			elif tax.charge_type == "On Previous Row Amount":
				current_tax_fraction = (tax_rate / 100.0) * \
					self.tax_doclist[cint(tax.row_id) - 1]\
						.tax_fraction_for_current_item
			
			elif tax.charge_type == "On Previous Row Total":
				current_tax_fraction = (tax_rate / 100.0) * \
					self.tax_doclist[cint(tax.row_id) - 1]\
						.grand_total_fraction_for_current_item
						
			print tax.account_head, tax_rate, current_tax_fraction

		return current_tax_fraction