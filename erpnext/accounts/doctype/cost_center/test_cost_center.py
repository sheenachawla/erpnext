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

base_cost_center = {
	"doctype": "Cost Center", "cost_center_name": "test_cost_center",
	"parent_cost_center": "Root - EW", "group_or_ledger": "Ledger", 
	"company_name": "East Wind Corporation"
}

base_gle = {'doctype': 'GL Entry', 'posting_date': '2012-06-02', 'debit': 100, \
	'company': 'East Wind Corporation', 'remarks': 'testing', \
	'voucher_type': 'Journal Voucher', 'voucher_no': 'JV001'
}

class TestCostCenter(TestBase):
	def test_cost_center_creation(self):
		self.session.insert(base_cost_center)
		self.assertTrue(self.session.db.exists("Cost Center", {'name': "test_cost_center - EW"}))
		
		self.assertRaises(webnotes.MandatoryError, self.session.insert_variants, \
			base_cost_center, [{'cost_center_name': 'EAST', 'parent_cost_center': ''}])
	
	def test_duplicate_cost_center(self):
		self.session.insert(base_cost_center)
		self.assertRaises(webnotes.NameError, self.session.insert, [base_cost_center])
		
	def test_root_cc(self):
		# root should not have parent
		self.session.insert_variants(base_cost_center, [{'group_or_ledger': 'Group', 'cost_center_name': 'test_cc_group'}])
		self.session.db.set_value("Cost Center", "Root - EW", "parent_cost_center", "test_cc_group - EW")
		account = self.session.get_controller('Cost Center', 'Root - EW')
		self.assertRaises(webnotes.MandatoryError, account.validate)

	def test_group_to_ledger(self):
		# group with child can not be converted to ledger
		cc = self.session.get_controller('Cost Center', 'Root - EW')
		self.assertRaises(webnotes.ValidationError, cc.convert_group_to_ledger)

		# successfull conversion (group to ledger)

		cc = self.session.insert(base_cost_center)
		self.assertEqual(cc.convert_group_to_ledger(), 1)

	def test_ledger_to_group(self):
		# successfull conversion (ledger to group)
		cc = self.session.insert(base_cost_center)
		self.assertEqual(cc.convert_ledger_to_group(), 1)

		# account with existing ledger entry can not be converted
		cc = base_cost_center.copy()
		cc.update({'cost_center_name': 'West'})
		cc = self.session.insert(cc)

		self.session.insert_variants(base_gle, [{'account': 'Sales - EW', 'cost_center': cc.doc['name']}])
		self.assertRaises(webnotes.ValidationError, cc.convert_ledger_to_group)

	def test_nsm_model(self):
		prev_rgt = self.get_rgt("Root - EW")
		self.session.insert(base_cost_center)
		self.assertEqual(self.get_rgt("Root - EW"), prev_rgt + 2)
		self.assertNsm('Cost Center', 'parent_cost_center', 'group_or_ledger')

	def get_rgt(self, cc):
		return self.session.db.get_value("Cost Center", cc, "rgt")
		
	def test_cc_deletion(self):		
		# successfull deletion
		cc = self.session.insert(base_cost_center)
		prev_rgt = self.get_rgt("Root - EW")
		self.session.delete_doc('Cost Center', cc.doc.name)

		self.assertFalse(self.session.db.exists('Cost Center', 'test_cost_center - EW'))
		self.assertEqual(self.get_rgt("Root - EW"), prev_rgt - 2)
		self.assertNsm('Cost Center', 'parent_cost_center', 'group_or_ledger')

	def test_cc_renaming(self):
		# successfull renaming
		self.session.insert(base_cost_center)

		self.session.rename_doc("Cost Center", "test_cost_center - EW", "test_cost_center_renamed - EW")

		self.assertFalse(self.session.db.exists("Cost Center", "test_cost_center - EW"))
		self.assertTrue(self.session.db.exists("Cost Center", "test_cost_center_renamed - EW"))