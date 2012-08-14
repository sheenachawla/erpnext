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
from webnotes.model.controller import DocListController

class PartyController(DocListController):
	def create_name(self, global_naming_key, naming_based_on, opp_dt):
		"""
			If naming based on customer/supplier name, check supplier/customer record with same name
			If exists, do not allow saving because it will conflict in party account
		"""
		if get_defaults(global_naming_key) == naming_based_on:
			party_name = self.doc[naming_based_on.lower().replace(' ', '_')]
			if webnotes.conn.exists(opp_dt, party_name):
				msgprint("You already have a %s with same name, please change the %s name"
				 	% (opp_dt, self.doc.doctype.lower()), raise_exception=webnotes.NameError)
			self.doc.name = party_name
		else:
			self.doc.name = make_autoname(self.doc.naming_series+'.#####')

	def validate_series(self, global_naming_key):
		""" 
			If party name by naming series, series field mandatory
		"""
		if get_defaults(global_naming_key) == 'Naming Series' and not self.doc.naming_series:
			msgprint("Series is Mandatory.", raise_exception=webnotes.MandatoryError)
			
	def update_credit_days_limit(self):
		webnotes.conn.sql("""
			update tabAccount 
			set credit_days = %s, credit_limit = %s
			where %s = %s
		"""% ('%s', '%s', self.doc.doctype.lower(), '%s'), 
		(self.doc.credit_days, self.doc.get('credit_limit', 0), self.doc.name))

	def get_party_group(self, fld):
		"""Returns Parent Account of customer/supplier from company master"""
		rg = webnotes.conn.get_value('Company', self.doc.company, fld)
		if not rg:
			msgprint("Assign default group for Receivables/Payables in company: %s" % \
				self.doc.company, raise_exception=webnotes.MandatoryError)
		return rg
		
	def create_account(self, account_args):
		""" 
			create party account head under
			parent group mentioned in company master
		"""
		if not webnotes.conn.get_value("Account", 
			{"account_name": self.doc.name, "company": self.doc.company}):
			args = {"account_name": self.doc.name, "group_or_ledger": "Ledger",
				"company": self.doc.company}
			args.update(account_args)
			account_head_name = webnotes.model.get_controller("GL Control").add_ac(args)
			webnotes.msgprint("""Account Head: "%s" created""" % account_head_name)

	def on_trash(self):
		self.delete_party_address_and_contact()
		self.delete_party_communication()
		self.delete_party_account()

	def delete_party_address_and_contact(self):
		for dt in ['Address', 'Contact']:
			webnotes.model.delete_doc(dt, webnotes.conn.get_value(dt, {self.doc.doctype.lower(): self.doc.name}))

	def delete_party_communication(self):
		webnotes.conn.sql("""delete from `tabCommunication` where %s = %s""", (self.doc.doctype.lower(), self.doc.name))

	def delete_party_account(self):
		"""delete party's ledger if exist and check balance before deletion"""
		acc = webnotes.conn.get_value("Account", {self.doc.doctype.lower(): self.doc.name})
		if acc:
			webnotes.model.delete_doc('Account', acc)
						
@webnotes.whitelist()
def get_contacts():
	return webnotes.conn.sql("""select name, first_name, last_name, email_id, 
		phone, mobile_no, department, designation, is_primary_contact 
		from tabContact
		where %s=%s and docstatus != 2
		order by is_primary_contact desc limit %s, %s""" % 
		(webnotes.form_dict.get('doctype').lower(), '%s', webnotes.form_dict.get("limit_start"), 
		webnotes.form_dict.get("limit_page_length")), webnotes.form_dict.get('name'), as_dict=1)

@webnotes.whitelist()
def get_addresses():		
	return webnotes.conn.sql("""select name, address_type, address_line1, address_line2, city, 
		state, country, pincode, fax, email_id, phone, is_primary_address, is_shipping_address 
		from tabAddress 
		where %s = %s and docstatus != 2 order by is_primary_address desc limit %s, %s""" %
		(webnotes.form_dict.get('doctype').lower(), '%s', webnotes.form_dict.get("limit_start"), 
		webnotes.form_dict.get("limit_page_length")), webnotes.form_dict.get('name'), as_dict=1)