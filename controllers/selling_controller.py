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
		self.validate_max_discount()
		self.validate_exchange_rate()
		self.validate_project()
		self.get_sales_team_contribution()
				
	def validate_order_type(self):
		if self.doc.order_type in ['Maintenance', 'Service']:
			item_type = "service item"
			item_type_field = "is_service_item"
		elif sself.doc.order_type == "Sales":
			item_type = "sales item"
			item_table_field = "is_sales_item"
			
		for item in self.doclist.get({"parentfield": self.item_table_field}):
			if webnotes.conn.get_value("Item", item.item_code, item_type_field) == "No":
				msgprint("You can not select non-%s: %s, if order type is %s" 
					% (item_type, item.item_code, self.doc.order_type), raise_exception=1)
				
	def validate_max_discount(self):
		for item in self.doclist.get({'parentfield': self.item_table_field}):
			max_discount = webnotes.conn.get_value('Item', item.item_code, 'max_discount')
			if max_discount and flt(item.discount) > flt(max_discount):
				msgprint(_("""Discount on row no: %s is greater than 
					max discount (%s) allowed for Item: %s""") 
					% (item.idx, max_discount, item.item_code), raise_exception=1)
	
	def validate_exchange_rate(self):
		def_currency = webnotes.conn.get_value("Company", self.doc.company, "default_currency")
		if not def_currency:
			msgprint(_("Default currency not mentioned in Company Master"),
				raise_exception=1)

		def _check(currency, conv_rate, currency_type):
			if not conv_rate or (currency == def_currency and flt(conv_rate) != 1.00) or \
					(currency != def_currency and flt(conv_rate) == 1.00):
				msgprint(_("""Please enter appropriate Exchange Rate for %s 
					currency (%s) to base currency (%s)""") 
					% (currency_type, self.doc.currency, def_currency), raise_exception=1)
					
		_check(self.doc.currency, self.doc.exchange_rate, 'Customer')
		_check(self.doc.price_list_currency, self.doc.plc_exchange_rate, 'Price List')
		
	def validate_project(self):
		if self.doc.get('project_name') and self.doc.customer != webnotes.conn.get_value(
				'Project', self.doc.project_name, 'customer'):
			msgprint("Project: %s does not associate with customer: %s" 
				% (self.doc.project_name, self.doc.customer), raise_exception=1)
				
	def get_sales_team_contribution(self):
		total_contribution = sum([d.allocated_percentage for d in 
			self.doclist.get({'parentfield': 'sales_team'})])
		for d in self.doclist.get({"parentfield": 'sales_team'}):
			d.allocated_percentage = d.allocated_percentage*100/total_contribution
			
	def append_default_taxes(self):
		"""called in on_map to add rows in tax table when they are missing"""
		if not (self.doc.customer or 
				len(self.doclist.get({"parentfield": "taxes_and_charges"}))):
			self.doc.taxes_and_charges_master = webnotes.conn.get_value(
				"Sales Taxes and Charges Master", {"is_default[0]": 1}, "name")
			
			if not self.doc.taxes_and_charges_master: return
			
			self.append_taxes()