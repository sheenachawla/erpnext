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
from webnotes.tests.test_base import TestBase

base_account = {
	"doctype": "Account", "account_name": "test_account",
	"parent_account": "Accounts Receivable - EW",
	"group_or_ledger": "Ledger", "debit_or_credit": "Debit",
	"is_pl_account": "No", "company": "East Wind Corporation"
}

base_gle = {'doctype': 'GL Entry', 'posting_date': '2012-06-02', 'debit': 100, \
	'company': 'East Wind Corporation', 'remarks': 'testing', \
	'voucher_type': 'Journal Voucher', 'voucher_no': 'JV001'
}

class TestAccount(TestBase):
	def test_account_creation(self):
		self.session.insert(base_account)
		self.assertTrue(self.session.db.exists("Account", {'name': "test_account - EW"}))
		
		# rate mandatory if account type is tax
		self.assertRaises(webnotes.MandatoryError, self.session.insert_variants, \
			base_account, [{'account_name': 'VAT', 'account_type': 'Tax'}])
		
	def test_parent_account(self):
		# parent account mandatory
		self.assertRaises(webnotes.MandatoryError, self.session.insert_variants, \
			base_account, [{'account_name': 'VAT', 'parent_account': ''}])
		
		# account itself assigned as parent
		self.session.insert_variants(base_account, [{'account_name': 'VAT'}])
		self.session.db.set_value('Account', 'VAT - EW', 'parent_account', 'VAT - EW')
		account = self.session.get_controller('Account', 'VAT - EW')
		self.assertRaises(webnotes.CircularLinkError, account.validate)
		
	def test_duplicate_account(self):
		self.session.insert(base_account)
		self.assertRaises(webnotes.NameError, self.session.insert, [base_account])
		
	def test_root_account(self):	
		# exactly 4 roots
		roots = self.session.db.sql("select name from `tabAccount` where company = \
			'East Wind Corporation' and ifnull(parent_account, '') = ''")
		self.assertEqual(len(roots), 4)
		
		# root should not have parent
		self.session.db.set_value("Account", "Income - EW", "parent_account", "Expenses - EW")
		account = self.session.get_controller('Account', 'Income - EW')
		self.assertRaises(webnotes.ValidationError, account.validate)
		
	def test_group_to_ledger(self):
		# group with child can not be converted to ledger
		acc = self.session.get_controller('Account', 'Expenses - EW')
		self.assertRaises(webnotes.ValidationError, acc.convert_group_to_ledger)
		
		# successfull conversion (group to ledger)

		acc = self.session.insert(base_account)
		self.assertEqual(acc.convert_group_to_ledger(), 1)
		
	def test_ledger_to_group(self):
		# successfull conversion (ledger to group)
		acc = self.session.insert(base_account)
		self.assertEqual(acc.convert_ledger_to_group(), 1)
		
		# account with account_type, customer or supplier can not be converted
		acc = base_account.copy()
		acc.update({'account_name': 'Convenience Charge', 'account_type': 'Chargeable'})
		acc = self.session.insert(acc)
		self.assertRaises(webnotes.ValidationError, acc.convert_ledger_to_group)
		
		# account with existing ledger entry can not be converted
		acc = base_account.copy()
		acc.update({'account_name': 'MD Electronics'})
		acc = self.session.insert(acc)
		
		gle = base_gle.copy()
		gle.update({'account': acc.doc['name']})
		self.session.insert(gle)
		self.assertRaises(webnotes.ValidationError, acc.convert_ledger_to_group)
		
	def test_nsm_model(self):
		prev_rgt = self.get_rgt("Application of Funds (Assets) - EW")
		self.session.insert(base_account)
		self.assertEqual(self.get_rgt("Application of Funds (Assets) - EW"), prev_rgt + 2)
		self.assertNsm('Account', 'parent_account', 'group_or_ledger')
		
	def get_rgt(self, acc):
		return self.session.db.get_value("Account", acc, "rgt")
					
	def test_account_deletion(self):		
		# successfull deletion
		acc = self.session.insert(base_account)
		prev_rgt = self.get_rgt("Application of Funds (Assets) - EW")
		self.session.delete_doc('Account', acc.doc.name)
		
		self.assertFalse(self.session.db.exists('Account', 'test_account - EW'))
		self.assertEqual(self.get_rgt("Application of Funds (Assets) - EW"), prev_rgt - 2)
		self.assertNsm('Account', 'parent_account', 'group_or_ledger')
		
		# if sle exists, could not be deleted		
		acc = self.session.insert(base_account)
		# gl entry
		self.session.insert_variants(base_gle, [{'account': acc.doc['name']}])
		
		self.assertRaises(webnotes.ValidationError, self.session.delete_doc, 'Account',
			acc.doc['name'])
		
		# if child exists, can not be deleted
		self.assertRaises(webnotes.ValidationError, self.session.delete_doc, \
			'Account', 'Accounts Receivable - EW')
			
	def test_account_renaming(self):
		# successfull renaming
		self.session.insert(base_account)
		
		self.session.rename_doc("Account", "test_account - EW", "test_account_renamed - EW")
		
		self.assertFalse(self.session.db.exists("Account", "test_account - EW"))
		self.assertTrue(self.session.db.exists("Account", {"name": "test_account_renamed - EW",\
		 	"account_name": "test_account_renamed"}))

		# new name should contain company abbr
		self.assertRaises(webnotes.NameError, rename_doc, "Account", \
			"test_account_renamed - EW", "test_account_renaming_without_abbr")