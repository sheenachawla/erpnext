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

from webnotes import _

import webnotes
import webnotes.model
from webnotes.utils import flt
from webnotes import msgprint
from webnotes.model.controller import DocListController

class SalesController(DocListController):
	def validate(self):
		if self.doc.docstatus != 2:
			self.validate_max_discount()
			self.validate_exchange_rate()
			self.validate_project()
			self.get_sales_team_contribution()
			self.calculate_totals()
		else:		
			from core.doctype.doctype_mapper.doctype_mapper import is_next_submitted
			is_next_submitted(self.doc.doctype, self.doc.name)
	
	def validate_max_discount(self):
		for d in self.doclist.get({'parentfield': self.item_table_fieldname}):
			max_discount = webnotes.conn.get_value('Item', d.item_code, 'max_discount')
			if max_discount and flt(d.discount) > flt(max_discount):
				msgprint(_("""Discount on row no: %s is greater than max dicount 
					(%s) allowed for Item: %s""") % (d.idx, max_discount, d.item_code), 
					raise_exception=webnotes.ValidationError)

	def validate_exchange_rate(self):
		def_currency = webnotes.conn.get_value('Company', self.doc.company,
			'default_currency')
		if not def_currency:
			msgprint(_("Default currency not mentioned in Company Master"),
				raise_exception=1)

		def _check(currency, conv_rate, currency_type):
			if not conv_rate or (currency == def_currency and flt(conv_rate) != 1.00) or \
					(currency != def_currency and flt(conv_rate) == 1.00):
				msgprint(_("""Please Enter Appropriate Exchange Rate for %s 
					currency (%s) to base currency (%s)""") % 
					(currency_type, self.doc.currency, def_currency), 
					raise_exception = webnotes.ValidationError)
					
		_check(self.doc.currency, self.doc.exchange_rate, 'Party')
		_check(self.doc.price_list_currency, self.doc.plc_exchange_rate, 'Price List')
		
	def get_sales_team_contribution(self):
		total_contribution = sum([d.allocated_percentage for d in \
			self.doclist.get({'parentfield': 'sales_team'})])
		for d in self.doclist.get({"parentfield": 'sales_team'}):
			d.allocated_percentage = d.allocated_percentage*100/total_contribution
		
	def is_next_submitted(self, nextdoc_types):
		"""
			check whether submitted next document type exists against current doc
			nextdoc_types is list of item tables of next doc
		"""
		for d in nextdoc_types:
			nextdoc = webnotes.conn.get_value(d, \
				{self.doc.doctype.lower().replace(' ', '_'): self.doc.name, \
				'docstatus': 1}, ['parent', 'parenttype'], as_dict=1)
			if nextdoc:
				msgprint(_("""Submitted %s: %s exists against this %s.""") % 
				(nextdoc.parenttype, nextdoc.parent, nextdoc.parenttype),
				raise_exception=webnotes.ValidationError)
				
	def validate_project(self):
		if self.doc.get('project_name'):
			if webnotes.conn.get_value('Project', self.doc.project_name, \
					'party') !=  self.doc.party:
				msgprint("Project: %s does not associate with party: %s" % 
					(self.doc.project_name, self.doc.party), 
					raise_exception=webnotes.ValidationError)
						
	def calculate_totals(self):
		# get tax 
		tax_masters = {}	
		def _get_tax_rate(row):
			if row.amount and row.taxes_and_charges:
				if not row.taxes_and_charges in tax_masters:
					taxlist = webnotes.model.get('Taxes and Charges', \
						row.taxes_and_charges).get({'parentfield': 'taxes_and_charges_accounts'})
				
					tax_masters[row.taxes_and_charges] = sum([d.rate for d in taxlist])
				
		def _get_tax_amount(row):
			if row.is_taxes_included:
				row.tax_amount = flt(row.amount) - \
					100*flt(row.amount)/(100+tax_masters.get(row.taxes_and_charges, 0))
				self.doc.net_total = flt(self.doc.net_total) + \
					flt(row.amount) - flt(row.tax_amount)
			else:
				row.tax_amount = flt(row.amount)*tax_masters.get(row.taxes_and_charges, 0)/100
				self.doc.net_total = flt(self.doc.net_total) + flt(row.amount)
		
		for d in self.doclist.get({'parentfield': self.item_table_fieldname}):
			d.amount = flt(d.qty)* flt(d.rate)
			if d.item_or_tax== 'Item':
				_get_tax_rate(d)
				_get_tax_amount(d)
			else:
				self.doc.tax_amount = self.doc.amount
			self.doc.taxes_and_charges_total = flt(self.doc.taxes_and_charges_total) + \
			 	flt(d.tax_amount)
			
		self.doc.grand_total = flt(self.doc.net_total) + flt(self.doc.taxes_and_charges_total)