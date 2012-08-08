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
from webnotes.utils import cstr, get_defaults
from webnotes.model.doc import Document, make_autoname
from webnotes.model.code import get_obj
from webnotes import msgprint
from controllers.party import PartyController

class CustomerController(PartyController):
	def autoname(self):
		self.create_name('cust_master_name', 'Customer Name', 'Supplier')
		
	def validate(self):
		self.validate_series('cust_master_name')

	def on_update(self):
		self.update_lead_status('Converted')
		self.create_customer_ledger()
		self.update_credit_days_limit()
		self.create_address_and_contact()

	def update_lead_status(self, status):
		if self.doc.lead_name:
			webnotes.conn.set_value('Lead', self.doc.lead_name, 'status', status)

	def create_customer_ledger(self):
		self.create_account({
			'parent_account': self.get_party_group('receivables_group'),
			'customer': self.doc.name
		})
	
	def create_address_and_contact(self):
		""" Create address and contact from lead details"""
		if self.doc.lead_name:
			lead_details = webnotes.conn.sql("""
				select lead_name, address_line1, address_line2, city, 
					country, state, pincode, phone, mobile_no, fax, email_id 
				from `tabLead` where name = %s
			""", self.doc.lead_name, as_dict = 1)[0]
				
			lead_details.update({
				'customer': self.doc.name,
				'customer_name': self.doc.customer_name,
				'address_type': 'Office', 
				'is_primary_address': 1,
				'first_name': lead_details['lead_name'],
				'is_primary_contact': 1
			})
			
			# create address
			self.create_doc('Address', lead_details, self.doc.name + "-Office")			
			# create contact
			self.create_doc('Contact', lead_details, lead_details['lead_name'])
			
	def create_doc(self, dt, values, dn):
		if not webnotes.conn.exists(dt, dn):
			webnotes.model.insert_variants(values, [{'doctype': dt}], ignore_fields=1)
	
	def on_trash(self):
		PartyController.on_trash(self)
		self.update_lead_status('Open')