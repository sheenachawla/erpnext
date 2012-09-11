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
from webnotes import _

from webnotes.utils import flt
from webnotes.utils.nestedset import NestedSetController


class AccountController(NestedSetController):
	def setup(self):
		self.nsm_parent_field = 'parent_account'

	def autoname(self):
		abbr = self.session.db.get_value('Company', self.doc.company, 'abbr')
		self.doc.name = self.doc.account_name.strip() + ' - ' + abbr
			
	def validate(self): 
		self.validate_rate_for_tax()
		self.validate_parent()
		self.validate_duplicate_account()
		self.validate_root_details()
		self.validate_mandatory()

	def validate_rate_for_tax(self):
		if self.doc.account_type == 'Tax' and not self.doc.tax_rate:
			self.session.msgprint(_("Please Enter Rate"), raise_exception=webnotes.MandatoryError)

	def validate_parent(self):
		"""
			Fetch Parent Details and validation for account not to be created under ledger
		"""
		if self.doc.parent_account:
			if self.doc.parent_account == self.doc.name:
				self.session.msgprint(_("You can not assign itself as parent account")
					, raise_exception=webnotes.CircularLinkError)
			elif not self.doc.is_pl_account or not self.doc.debit_or_credit:
				par = self.session.db.get_value("Account", \
					self.doc.parent_account, ["is_pl_account", "debit_or_credit"])
				self.doc.is_pl_account = par[0]
				self.doc.debit_or_credit = par[1]
		elif self.doc.account_name not in ['Income','Source of Funds (Liabilities)',\
		 	'Expenses','Application of Funds (Assets)']:
			self.session.msgprint(_("Parent Account is mandatory"), raise_exception=webnotes.MandatoryError)
	
	def validate_duplicate_account(self):
		"""Account name must be unique"""
		if (self.doc.__islocal or not self.doc.name) \
				and self.session.db.exists("Account", {"account_name": self.doc.account_name, \
				"company": self.doc.company}):
			self.session.msgprint(_("Account Name already exists, please rename"), raise_exception=webnotes.NameError)
				
	def validate_root_details(self):
		#does not exists parent
		if self.doc.account_name in ['Income','Source of Funds (Liabilities)', \
			'Expenses', 'Application of Funds (Assets)'] and self.doc.parent_account:
			self.session.msgprint(_("You can not assign parent for root account"), raise_exception=webnotes.ValidationError)

		# Debit / Credit
		if self.doc.account_name in ['Income','Source of Funds (Liabilities)']:
			self.doc.debit_or_credit = 'Credit'
		elif self.doc.account_name in ['Expenses','Application of Funds (Assets)']:
			self.doc.debit_or_credit = 'Debit'
				
		# Is PL Account 
		if self.doc.account_name in ['Income','Expenses']:
			self.doc.is_pl_account = 'Yes'
		elif self.doc.account_name in ['Source of Funds (Liabilities)','Application of Funds (Assets)']:
			self.doc.is_pl_account = 'No'

	def validate_mandatory(self):
		if not self.doc.debit_or_credit or not self.doc.is_pl_account:
			self.session.msgprint(_("'Debit or Credit' and 'Is PL Account' field is mandatory")
				, raise_exception=webnotes.MandatoryError)

	def convert_group_to_ledger(self):
		# if child exists
		if self.session.db.exists("Account", {"parent_account": self.doc.name}):
			self.session.msgprint(_("""Account: %s has existing child. You can not convert
				this account to ledger.	To proceed, move those children under
				another parent and try again,""") 
				% self.doc.name, raise_exception=webnotes.ValidationError)
		else:
			self.session.db.set(self.doc, 'group_or_ledger', 'Ledger')
			return 1
			
	def convert_ledger_to_group(self):
		if self.check_gle_exists():
			self.session.msgprint(_("Account with existing transaction can not be converted to group."), 
				raise_exception=webnotes.ValidationError)
		elif self.doc.account_type:
			self.session.msgprint(_("Cannot convert to Group because Account Type is selected."), 
				raise_exception=webnotes.ValidationError)
		else:
			self.session.db.set(self.doc, 'group_or_ledger', 'Group')
			return 1

	def check_gle_exists(self):
		return self.session.db.exists("GL Entry", {"account": self.doc.name})

	def on_update(self):
		self.update_nsm_model()

	def update_nsm_model(self):
		import webnotes
		import webnotes.utils.nestedset
		webnotes.utils.nestedset.update_nsm(self)
					
	def on_trash(self):
		self.validate_before_trash()
		# rebuild tree
		from webnotes.utils.nestedset import update_remove_node
		update_remove_node('Account', self.doc.name)

	def validate_before_trash(self):
		"""Account with with existing gl entries cannot be inactive"""
		if self.check_gle_exists():
			self.session.msgprint(_("Account with existing transaction \
				(Sales Invoice / Purchase Invoice / Journal Voucher) can not be trashed")
				, raise_exception=webnotes.ValidationError)
		if self.session.db.exists("Account", {'parent_account': self.doc.name}):
			self.session.msgprint(_("Child account exists for this account. You can not trash this account.")
				, raise_exception=webnotes.ValidationError)
	
	def on_rename(self,newdn,olddn):
		new_name = newdn.split(" - ")
		company_abbr = self.session.db.get_value("Company", self.doc.company, "abbr")
		
		if new_name[-1].lower() != company_abbr.lower():
			self.session.msgprint(_("Please add company abbreviation: <b>%s</b> in new account name") \
				% company_abbr, raise_exception=webnotes.NameError)
		else:
			new_acc_name = " - ".join(new_name[:-1])
			self.session.db.set_value("Account", olddn, "account_name", new_acc_name)
