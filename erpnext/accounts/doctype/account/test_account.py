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

base_account = {
	"doctype": "Account", "account_name": "test_account",
	"parent_account": "Accounts Receivable - EW",
	"group_or_ledger": "Ledger", "debit_or_credit": "Debit",
	"is_pl_account": "No", "company": "East Wind Corporation"
}

base_gle = {'doctype': 'GL Entry', 'posting_date': '2012-06-02', 'debit': 100, \
	'company': 'East Wind Corporation', 'fiscal_year': '2012-2013', 'remarks': 'testing', \
	'voucher_type': 'Journal Voucher', 'voucher_no': 'JV001', 'is_cancelled': 'No'
}

class TestAccount(TestBase):
	def test_account_creation(self):
		cust = base_account.copy()
		webnotes.model.insert(cust)
		self.assertTrue(webnotes.conn.exists("Account", {'name': "test_account - EW"}))
		
		# rate mandatory if account type is tax
		cust = base_account.copy()
		cust.update({'account_name': 'VAT', 'account_type': 'Tax'})
		self.assertRaises(webnotes.MandatoryError, webnotes.model.insert, [cust])
		
	def test_parent_account(self):
		# parent account mandatory
		cust = base_account.copy()
		cust.update({'account_name': 'VAT', 'parent_account': ''})
		self.assertRaises(webnotes.MandatoryError, webnotes.model.insert, [cust])
		
		# account itself assigned as parent
		cust = base_account.copy()
		cust.update({'account_name': 'VAT', 'parent_account': 'VAT - EW'})
		webnotes.model.insert(cust)
		
		account = webnotes.model.get_controller('Account', 'VAT - EW')
		self.assertRaises(webnotes.CircularLinkError, account.validate)
		
	def test_duplicate_account(self):
		acc1 = base_account.copy()
		webnotes.model.insert(acc1)
		
		acc2 = base_account.copy()
		self.assertRaises(webnotes.NameError, webnotes.model.insert, [acc2])
		
	def test_root_account(self):	
		# exactly 4 roots
		roots = webnotes.conn.sql("select name from `tabAccount` where company = \
			'East Wind Corporation' and ifnull(parent_account, '') = ''")
		self.assertEqual(len(roots), 4)
		
		# root should not have parent
		webnotes.conn.set_value("Account", "Income - EW", "parent_account", "Expenses - EW")
		account = webnotes.model.get_controller('Account', 'Income - EW')
		self.assertRaises(webnotes.ValidationError, account.validate)
		
	def test_group_to_ledger(self):
		# group with child can not be converted to ledger
		acc = webnotes.model.get_controller('Account', 'Expenses - EW')
		self.assertRaises(webnotes.ValidationError, acc.convert_group_to_ledger)
		
		# successfull conversion (group to ledger)
		acc = base_account.copy()
		acc = webnotes.model.insert(acc)
		self.assertEqual(acc.convert_group_to_ledger(), 1)
		
	def test_ledger_to_group(self):
		# successfull conversion (ledger to group)
		acc = base_account.copy()
		acc = webnotes.model.insert(acc)
		self.assertEqual(acc.convert_ledger_to_group(), 1)
		
		# account with account_type, customer or supplier can not be converted
		acc = base_account.copy()
		acc.update({'account_name': 'Convenience Charge', 'account_type': 'Chargeable'})
		acc = webnotes.model.insert(acc)
		self.assertRaises(webnotes.ValidationError, acc.convert_ledger_to_group)
		
		# account with existing ledger entry can not be converted
		acc = base_account.copy()
		acc.update({'account_name': 'MD Electronics'})
		acc = webnotes.model.insert(acc)
		
		gle = base_gle.copy()
		gle.update({'account': acc.doc['name']})
		acc = webnotes.model.insert(gle)
		self.assertRaises(webnotes.ValidationError, acc.doc.convert_ledger_to_group)
		
	def test_nsm_model(self):
		prev_rgt = self.get_rgt("Application of Funds (Assets) - EW")
		webnotes.model.insert(base_account.copy())
		self.assertEqual(self.get_rgt("Application of Funds (Assets) - EW"), prev_rgt + 2)
		self.assertNsm('Account', 'parent_account', 'group_or_ledger')
		
	def get_rgt(self, acc):
		return webnotes.conn.get_value("Account", acc, "rgt")
		
	def test_credit_limit(self):
		acc = base_account.copy()
		acc.update({'credit_limit': 100000})
		acc_controller = webnotes.model.insert(acc)
		self.assertRaises(webnotes.ValidationError, acc_controller.check_credit_limit, \
			acc_controller.doc.name, acc_controller.doc.company, 200000)
			
	def test_account_deletion(self):		
		# successfull deletion
		acc = base_account.copy()
		acc = webnotes.model.insert(acc)
		prev_rgt = self.get_rgt("Application of Funds (Assets) - EW")
		webnotes.model.delete_doc('Account', acc.doc.name)
		
		self.assertFalse(webnotes.conn.exists('Account', 'test_account - EW'))
		self.assertEqual(self.get_rgt("Application of Funds (Assets) - EW"), prev_rgt - 2)
		self.assertNsm('Account', 'parent_account', 'group_or_ledger')
		
		# if sle exists, could not be deleted		
		acc = base_account.copy()
		acc = webnotes.model.insert(acc)
		# gl entry
		gle = base_gle.copy()
		gle.update({'account': acc.doc['name']})
		webnotes.model.insert(gle)
		
		self.assertRaises(webnotes.ValidationError, webnotes.model.delete_doc, 'Account',
			acc.doc['name'])
		
		# if child exists, can not be deleted
		self.assertRaises(webnotes.ValidationError, webnotes.model.delete_doc, \
			'Account', 'Accounts Receivable - EW')
			
	def test_account_renaming(self):
		# successfull renaming
		acc = base_account.copy()
		webnotes.model.insert(acc)
		
		from webnotes.model.rename_doc import rename_doc
		rename_doc("Account", "test_account - EW", "test_account_renamed - EW")
		
		self.assertFalse(webnotes.conn.exists("Account", "test_account"))
		self.assertTrue(webnotes.conn.exists("Account", {"name": "test_account_renamed - EW",\
		 	"account_name": "test_account_renamed"}))

		# new name should contain company abbr
		self.assertRaises(webnotes.NameError, rename_doc, "Account", \
			"test_account_renamed - EW", "test_account_renaming_without_abbr")