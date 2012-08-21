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
from webnotes.utils import flt, fmt_money, getdate
from webnotes import msgprint
from webnotes.model.controller import DocListController
from webnotes.model import get_controller

class GLEntryController(DocListController):
	def validate(self):	
		"""	validates gl entry values"""
		self.check_mandatory()
		self.validate_zero_value_transaction()
		self.pl_must_have_cost_center()
		self.validate_posting_date()
		self.check_credit_limit()
		self.no_opening_entry_against_pl_account()
	
	def check_mandatory(self):
		# Following fields are mandatory in GL Entry
		mandatory = ['account', 'voucher_type','voucher_no', 'company', 'posting_date']
		for k in mandatory:
			if not self.doc.get(k):
				msgprint("%s is mandatory for GL Entry" % k,
					raise_exception=webnotes.MandatoryError)
				
	def validate_zero_value_transaction(self):
		if not (flt(self.doc.debit) or flt(self.doc.credit)):
			msgprint("GL Entry: Debit or Credit amount is mandatory for %s" 
				% self.doc.account, raise_exception=webnotes.ValidationError)
					
	def pl_must_have_cost_center(self):
		"""
			Cost center is required only if transaction made against pl account
		"""
		if webnotes.conn.exists('Account', {'name': self.doc.account, 'is_pl_account': 'Yes'}):
			if not self.doc.cost_center and self.doc.voucher_type != 'Period Closing Voucher':
				msgprint("Cost Center must be specified for PL Account: %s" \
					% self.doc.account, raise_exception=webnotes.MandatoryError)
		else: # not pl
			if self.doc.cost_center:
				self.doc.cost_center = ''
		
	def check_credit_limit(self):
		"""Total outstanding can not be greater than credit limit for any time for any customer"""
		if self.doc.party:
			tot_outstanding = 0
			dbcr = webnotes.conn.sql("select sum(debit), sum(credit) from `tabGL Entry` \
				where party = '%s' and company = %s", (self.doc.party, self.doc.company))
			if dbcr:
				tot_outstanding = flt(dbcr[0][0]) - flt(dbcr[0][1]) + flt(self.doc.debit) - flt(self.doc.credit)

			get_controller('Party',self.doc.party).check_credit_limit(self.doc.company, tot_outstanding)

	def no_opening_entry_against_pl_account(self):
		if self.doc.is_opening=='Yes':
			if webnotes.conn.get_value('Account', self.doc.account, 'is_pl_account') == 'Yes':
				msgprint("For opening balance entry account can not be a PL account"\
					, raise_exception=webnotes.ValidationError)
		
	def on_update(self, adv_adj=0):
		# Account must be ledger, active and not freezed
		self.validate_account_details(adv_adj)
		# Posting date must be after freezing date
		self.check_freezing_date(adv_adj)
		
	def validate_account_details(self, adv_adj):
		"""Account must be ledger, active and not freezed"""
		
		acc = webnotes.conn.get_value('Account', self.doc.account, \
			['group_or_ledger', 'freeze_account', 'company'])
		
		# Checks whether Account is a ledger
		if acc[0]=='Group':
			msgprint("Ledger Entry not allowed against Account %s as it is Group" 
				% self.doc.account, raise_exception=webnotes.ValidationError)
			
		# Account has been freezed for other users except account manager
		if acc[1]== 'Yes' and not adv_adj and 'Accounts Manager' not in webnotes.user.get_roles():
			msgprint("Account %s has been freezed. Only Accounts Manager can do \
				transaction against this account." % self.doc.account, raise_exception=webnotes.ValidationError)
			
		# Check whether account is within the company
		if acc[2] != self.doc.company:
			msgprint("Account: %s does not belong to the company: %s" 
				% (self.doc.account, self.doc.company), raise_exception=webnotes.ValidationError)
			
	def check_freezing_date(self, adv_adj):
		"""If posting date is before freezing date, GL Entry restricted to authorized person"""
		if not adv_adj:
			acc_frozen_info = webnotes.conn.get_value('Global Defaults', None, ['acc_frozen_upto', 'bde_auth_role'], as_dict=1)
			if acc_frozen_info and acc_frozen_info['acc_frozen_upto']:
				if getdate(self.doc.posting_date) <= getdate(acc_frozen_info['acc_frozen_upto']) \
					and not acc_frozen_info['bde_auth_role'] in webnotes.user.get_roles():
					msgprint("You are not authorized to do/modify back dated accounting entries before %s." 
						% getdate(acc_frozen_info['acc_frozen_upto']).strftime('%d-%m-%Y'), raise_exception=webnotes.ValidationError)