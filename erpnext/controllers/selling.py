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
from webnotes.utils import flt
from webnotes import msgprint
from webnotes.model.controller import DocListController

class SalesController(DocListController):
	def validate(self):
		self.validate_items()
		self.validate_max_discount()
		self.validate_conversion_rate()	
		self.validate_project()
		self.get_sales_team_contribution()
	
	def validate_max_discount(self):
		for d in self.doclist.get({'parentfield': self.item_table_fieldname}):
			max_discount = webnotes.conn.get_value('Item', d.item_code, 'max_discount')
			if max_discount and flt(d.discount) > flt(max_discount):
				msgprint("""Discount on row no: %s is greater than max dicount 
					(%s) allowed to item: %s""" % (d.idx, max_discount, d.item_code), 
					raise_exception=webnotes.ValidationError)

	def validate_conversion_rate(self):
		def_currency = webnotes.conn.get_value('Company', self.doc.company, 'default_currency')
		if not def_currency:
			msgprint("Default currency not mentioned in Company Master"
				, raise_exception=webnotes.ValidationError)

		def _check(currency, conv_rate, currency_type):
			if not conv_rate or (currency == def_currency and flt(conv_rate) != 1.00) or \
					(currency != def_currency and flt(conv_rate) == 1.00):
				msgprint("""Please Enter Appropriate Conversion Rate for %s 
					currency (%s) to base currency (%s)""" % 
					(currency_type, self.doc.currency, def_currency), 
					raise_exception = webnotes.ValidationError)
					
		_check(self.doc.currency, self.doc.conversion_rate, 'customer')
		_check(self.doc.price_list_currency, self.doc.plc_conversion_rate, 'price list')
		
	def get_sales_team_contribution(self):
		total_contribution = sum([d.allocated_percentage for d in \
			self.doclist.get({'parentfield': 'sales_team'})])
		for d in self.doclist.get({"parentfield": 'sales_team'}):
			d.allocated_percentage = d.allocated_percentage*100/total_contribution
		
	def check_if_nextdoc_exists(self, nextdoc_types, event = 'cancel'):
		"""
			check whether submitted next document type exists against current doc
			nextdoc_types is list of item tables of next doc
		"""
		for d in nextdoc_types:
			nextdoc = webnotes.conn.get_value(d, \
				{self.doc.doctype.lower(): self.doc.name, 'docstatus': 1}, \
				['parent', 'parenttype'], as_dict=1)
			if nextdoc:
				msgprint("""Submitted %s: %s exists against this %s. 
				To %s this document first cancel %s""" % 
				(nextdoc['parenttype'], nextdoc['parent'], self.doc.doctype, event, \
				nextdoc['parenttype']), raise_exception=webnotes.ValidationError)
				

	def validate_items(self):
		if self.doc.fields.get('order_type'):
			for d in self.doclist.get({'parentfield': self.item_table_fieldname}):
				self.validate_item_type(d.item_code)

				
	def validate_item_type(self, item_code):
		item_type = webnotes.conn.get_value('Item', item_code, \
			['is_sales_item', 'is_service_item'], as_dict=1)
		if self.doc.order_type == 'Sales' and item_type['is_sales_item'] == 'No':
			msgprint("Item: %s is not a sales item" % 
			item_code, raise_exception=webnotes.ValidationError)
		elif self.doc.order_type == 'Maintenance' and item_type['is_service_item'] == 'No':
			msgprint("Item %s is not a maintenance item" %
				item_code, raise_exception=webnotes.ValidationError)
				

	def validate_project(self):
		if self.doc.project_name:
			if webnotes.conn.get_value('Project', self.doc.project_name, \
					'party') !=  self.doc.party:
				msgprint("Project: %s does not associate with party: %s" % 
					(self.doc.project_name, self.doc.party), 
					raise_exception=webnotes.ValidationError)