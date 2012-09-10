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

import webnotes
import webnotes.model.controller

class AddressController(webnotes.model.controller.DocListController):
	def autoname(self):
		if self.doc.party:
			self.doc.name = self.doc.party + '-' + self.doc.address_type

	def validate(self):
		# need to be rewritten
		pass
		#self.validate_primary_address()
		#self.validate_shipping_address()
	
	def validate_primary_address(self):
		"""Validate that there can only be one primary address for particular customer, supplier"""
		if self.doc.is_primary_address == 1:
			if self.doc.customer: 
				webnotes.conn.sql("update tabAddress set is_primary_address=0 where customer = '%s'" % (self.doc.customer))
			elif self.doc.supplier:
				webnotes.conn.sql("update tabAddress set is_primary_address=0 where supplier = '%s'" % (self.doc.supplier))
			elif self.doc.sales_partner:
				webnotes.conn.sql("update tabAddress set is_primary_address=0 where sales_partner = '%s'" % (self.doc.sales_partner))
		elif not self.doc.is_shipping_address:
			if self.doc.customer: 
				if not webnotes.conn.sql("select name from tabAddress where is_primary_address=1 and customer = '%s'" % (self.doc.customer)):
					self.doc.is_primary_address = 1
			elif self.doc.supplier:
				if not webnotes.conn.sql("select name from tabAddress where is_primary_address=1 and supplier = '%s'" % (self.doc.supplier)):
					self.doc.is_primary_address = 1
			elif self.doc.sales_partner:
				if not webnotes.conn.sql("select name from tabAddress where is_primary_address=1 and sales_partner = '%s'" % (self.doc.sales_partner)):
					self.doc.is_primary_address = 1

				
	def validate_shipping_address(self):
		"""Validate that there can only be one shipping address for particular customer, supplier"""
		if self.doc.is_shipping_address == 1:
			if self.doc.customer: 
				webnotes.conn.sql("update tabAddress set is_shipping_address=0 where customer = '%s'" % (self.doc.customer))
			elif self.doc.supplier:
				webnotes.conn.sql("update tabAddress set is_shipping_address=0 where supplier = '%s'" % (self.doc.supplier))			
			elif self.doc.sales_partner:
				webnotes.conn.sql("update tabAddress set is_shipping_address=0 where sales_partner = '%s'" % (self.doc.sales_partner))			
