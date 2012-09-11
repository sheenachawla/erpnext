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
import webnotes.model
from webnotes.utils import cstr, get_defaults, flt, fmt_money
from webnotes.model.doc import Document, make_autoname
from webnotes import msgprint, _
from webnotes.model.controller import DocListController

class PartyController(DocListController):	
	def on_update(self):
		if self.doc.party_type == 'Customer':
			self.update_lead_status('Converted')
			self.create_address_and_contact()

	def update_lead_status(self, status):
		if self.doc.lead_id:
			webnotes.conn.set_value('Lead', self.doc.lead_id, 'status', status)

	def create_address_and_contact(self):
		""" Create address and contact from lead details"""
		if self.doc.lead_id:
			lead_details = webnotes.conn.sql("""
				select lead_name, address_line1, address_line2, city, 
				country, state, pincode, phone, mobile_no, fax, email_id 
				from `tabLead` where name = %s""", self.doc.lead_id)[0]

			lead_details.update({
				'party': self.doc.name,
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
			webnotes.model.insert_variants(values, [{'doctype': dt}])
			
	def check_credit_limit(self, company, current_amount=0):
		"""checked only for customers i.e. in sales transaction"""
		credit_limit = flt(self.doc.credit_limit or \
			webnotes.conn.get_value('Company', company, 'credit_limit'))
		
		prev_outstanding = webnotes.conn.sql("""select sum(debit) - sum(credit) \
			from `tabGL Entry` where party = %s and company = %s""", 
			(self.doc.name, company), as_dict=False)[0][0]
		total_outstanding = flt(prev_outstanding) + flt(current_amount)
		
		# if outstanding greater than credit limit and not authorized person
		if credit_limit > 0 and total_outstanding > credit_limit and \
				not self.get_authorized_user():
			msgprint(_("Total Outstanding amount (%s) for <b>%s</b> can not be \
				greater than Credit Limit (%s). To change your Credit Limit settings, \
				please update the <b>%s</b>") % \
				(fmt_money(total_outstanding), self.doc.name, fmt_money(credit_limit), 
				_(self.doc.credit_limit and 'Party' or 'Company')),
				raise_exception=webnotes.ValidationError)

	def get_authorized_user(self):
		if webnotes.conn.get_value('Global Defaults', None, 'credit_controller') \
				in webnotes.user.get_roles():
			return 1

	def on_trash(self):
		"""
		 	Delete address, contacts and communication related to Party
			Update lead statusto Open, party created from Lead
		"""
		self.delete_party_address_and_contact()
		self.delete_party_communication()
		if self.doc.party_type == 'Customer':
			self.update_lead_status('Open')

	def delete_party_address_and_contact(self):
		for dt in ['Address', 'Contact']:
			webnotes.model.delete_doc(dt, webnotes.conn.get_value(dt, {'party': self.doc.name}))

	def delete_party_communication(self):
		webnotes.conn.sql("""delete from `tabCommunication` \
			where party = %s""", self.doc.name)
						
@webnotes.whitelist()
def get_contacts():
	return webnotes.conn.sql("""select name, first_name, last_name, email_id, 
		phone, mobile_no, department, designation, is_primary_contact 
		from tabContact
		where party=%s and docstatus != 2
		order by is_primary_contact desc limit %s, %s""" % 
		('%s', webnotes.form.get("limit_start"), 
		webnotes.form.get("limit_page_length")), webnotes.form.get('name'))

@webnotes.whitelist()
def get_addresses():		
	return webnotes.conn.sql("""
		select 
			name, address_type, address_line1, 
			address_line2, city, state, country, pincode, fax, email_id, phone,
			is_primary_address, is_shipping_address 
		from 
			tabAddress 
		where 
			party = %s and docstatus != 2 
		order by is_primary_address desc 
		limit %s, %s""" %
		('%s', webnotes.form.get("limit_start"), 
		webnotes.form.get("limit_page_length")), webnotes.form.get('name'))
