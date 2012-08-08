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
		if get_defaults(global_naming_key) == naming_based_on:
			party_name = self.doc.fields[naming_based_on.lower().replace(' ', '_')]
			if webnotes.conn.exists(opp_dt, party_name):
				msgprint("You already have a %s with same name, please change the %s name"
				 	% (opp_dt, self.doc.doctype.lower()), raise_exception=webnotes.NameError)
			self.doc.name = party_name
		else:
			self.doc.name = make_autoname(self.doc.naming_series+'.#####')

	def validate_series(self, global_naming_key):
		""" If master name by naming series, series field mandatory"""
		if get_defaults(global_naming_key) == 'Naming Series' and not self.doc.naming_series:
			msgprint("Series is Mandatory.", raise_exception=webnotes.MandatoryError)
			
	def update_credit_days_limit(self):
		webnotes.conn.sql("""
			update tabAccount 
			set credit_days = %s, credit_limit = %s
			where master_type = %s and master_name = %s
		""", (self.doc.credit_days, self.doc.fields.get('credit_limit', 0), self.doc.doctype, self.doc.name))

	def get_party_group(self, company, fld):
		"""Returns Parent Account of customer/supplier from company master"""
		rg = webnotes.conn.get_value('Company', company, fld)
		if not rg:
			msgprint("Assign default group for Receivables/Payables in company: %s" % \
				company, raise_exception=webnotes.MandatoryError)
		return rg
		
	def create_account(self, det):
		""" 
			create party account head under
			parent group mentioned in company master
		"""
		acc_details = {
			'account_name':self.doc.name,
			'group_or_ledger':'Ledger', 
			'master_type':self.doc.doctype,
			'master_name':self.doc.name
		}
		acc_details.update(det)
		if not webnotes.conn.get_value('Account', 
			{"account_name": acc_details['account_name'], "company": acc_details['company']}):
			ac = get_obj('GL Control').add_ac(cstr(acc_details))
			msgprint("Account Head: %s created" % ac)
			return ac

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
		"""delete customer's ledger if exist and check balance before deletion"""
		acc = webnotes.conn.get_value("Account", {"master_type": self.doc.doctype, "master_name": self.doc.name})
		if acc:
			webnotes.model.delete_doc('Account', acc)
			
	def on_rename(self, newdn, olddn):
		"""
			update party_name in all documents, if party id is set by party name
		"""
		naming = {
			'Customer': {'global_key': 'cust_master_name', 'based_on': 'customer_name'},
			'Supplier': {'global_key': 'supp_master_name','based_on': 'supplier_name'},
		}
		if get_defaults().get(naming[self.doc.doctype]['global_key']) == naming[self.doc.doctype]['based_on']:
			dt_list = webnotes.conn.sql("""select dt.name from `tabDocField` df, `tabDocType` dt 
				where df.fieldname = %s and df.parent != %s and df.parent = dt.name and ifnull(dt.issingle, 0)=0
			""", (naming[self.doc.doctype]['based_on'], self.doc.doctype))
			
			for dt in dt_list:
				webnotes.conn.sql("update `tab%s` set %s = %s where %s = %s" 
					% (dt[0], naming[self.doc.doctype]['based_on'], '%s', naming[self.doc.doctype]['based_on'], '%s')
					, (newdn, olddn))

		#update new master_name in party account
		webnotes.conn.sql("update `tabAccount` set master_name = %s \
			where master_name = %s", (newdn,olddn))
			
@webnotes.whitelist()
def get_contacts():
	return webnotes.conn.sql("""select name, first_name, last_name, email_id, phone, mobile_no,
	department, designation, is_primary_contact from tabContact
	where %s=%s and docstatus != 2
	order by is_primary_contact desc limit %s, %s""" % (webnotes.form_dict.get('doctype').lower(), 
		'%s', webnotes.form_dict.get("limit_start"), 
		webnotes.form_dict.get("limit_page_length")),
		webnotes.form_dict.get('name'), as_dict=1)