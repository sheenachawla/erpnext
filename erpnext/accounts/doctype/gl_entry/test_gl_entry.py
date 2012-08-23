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
from webnotes.tests.test_base import TestBase
from webnotes.model import get_controller

base_party = {
	'doctype': 'Party', 'name': 'test_party', 'party_type': 'Customer'
}

base_acc = {
	"doctype": "Account", "group_or_ledger": "Ledger", "debit_or_credit": "Debit",
	"is_pl_account": "No", "company": "East Wind Corporation"
}

base_cost_center = {
	"doctype": "Cost Center", "cost_center_name": "test_cost_center",
	"parent_cost_center": "Root - EW", "group_or_ledger": "Ledger", 
	"company_name": "East Wind Corporation"
}

base_gle = {'doctype': 'GL Entry', 'posting_date': '2012-06-02', \
	'debit': 100, 'company': 'East Wind Corporation', 'remarks': 'testing', \
	'voucher_type': 'Journal Voucher', 'voucher_no': 'JV001'
}

class TestGLEntry(TestBase):
	def setUp(self):
		super(TestGLEntry, self).setUp()
		webnotes.model.insert(base_party)
		webnotes.model.insert_variants(base_acc, \
			[{'account_name': 'test_income', 'parent_account': 'Direct Income - EW', 'is_pl_account': 'Yes'}])
		webnotes.model.insert_variants(base_acc, \
			[{'account_name': 'test_receivable', 'parent_account': 'Accounts Receivable - EW'}])
		webnotes.model.insert_variants(base_acc, \
			[{'account_name': 'test_bank_account', 'parent_account': 'Bank Accounts - EW'}])
		webnotes.model.insert(base_cost_center)
		
		
	def test_mandatory(self):
		mandatory = ['account', 'voucher_type','voucher_no', 'company', 'posting_date']
		for fld in mandatory:
			gle = base_gle.copy()
			gle.update({'account': 'test_receivable - EW'})
			gle.pop(fld)
			self.assertRaises(webnotes.MandatoryError, webnotes.model.insert, [gle])
		
	def test_zero_value_trasaction(self):
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert_variants, \
			base_gle, [{'account': 'test_receivable - EW', 'debit': 0}])
			
	def test_cost_center_against_pl_acc(self):
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert_variants, \
			base_gle, [{'account': 'test_income - EW'}])
			
		webnotes.model.insert_variants(base_gle, [{'account': 'test_income - EW', \
			'cost_center': 'test_cost_center - EW'}])
		self.assertTrue(webnotes.conn.exists('GL Entry', {'account': 'test_income - EW'}))
		
	def test_entry_against_group(self):
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert_variants, \
			base_gle, [{'account': 'Accounts Receivable - EW'}])
	
	def test_entry_against_frozen_account(self):
		webnotes.model.insert_variants(base_acc, [{'account_name': 'frozen_account', \
			'parent_account': 'Accounts Receivable - EW', 'freeze_account': 'Yes'}])
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert_variants, \
			base_gle, [{'account': 'frozen_account - EW'}])
			
		# allowed to accounts manager role
		webnotes.model.insert({'doctype': 'UserRole', 'role': 'Accounts Manager', 'parent': 'Administrator'})
		webnotes.model.insert_variants(base_gle, [{'account': 'frozen_account - EW'}])
		
	def test_entry_before_frozen_date(self):
		webnotes.conn.set_value('Global Defaults', None, 'acc_frozen_upto', '2011-03-31')
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert_variants, \
			base_gle, [{'account': 'test_receivable - EW', 'posting_date': '2011-01-01'}])
			
		# allowed to the role specified in Global Defaults
		webnotes.conn.set_value('Global Defaults', None, 'bde_auth_role', 'Accounts Manager')
		webnotes.model.insert({'doctype': 'UserRole', 'role': 'Accounts Manager', 'parent': 'Administrator'})
		webnotes.model.insert_variants(base_gle, [{'account': 'test_receivable - EW', 'posting_date': '2011-01-01'}])
		
	def test_credit_limit(self):
		webnotes.model.insert_variants(base_party, [{'name': 'party_with_credit_limit', 'credit_limit': 50}])
		self.assertRaises(webnotes.ValidationError, webnotes.model.insert_variants, \
			base_gle, [{'account': 'test_receivable - EW', 'party': 'party_with_credit_limit'}])