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
		webnotes.model.insert(base_cost_center)
		self.assertTrue(webnotes.conn.exists("Cost Center", {'name': "test_cost_center - EW"}))
		
		self.assertRaises(webnotes.MandatoryError, webnotes.model.insert_variants, \
			base_cost_center, [{'cost_center_name': 'EAST', 'parent_cost_center': ''}])
	
	def test_duplicate_cost_center(self):
		webnotes.model.insert(base_cost_center)
		self.assertRaises(webnotes.NameError, webnotes.model.insert, [base_cost_center])
		
	def test_root_cc(self):
		# root should not have parent
		webnotes.model.insert_variants(base_cost_center, [{'group_or_ledger': 'Group', 'cost_center_name': 'test_cc_group'}])
		webnotes.conn.set_value("Cost Center", "Root - EW", "parent_cost_center", "test_cc_group - EW")
		account = webnotes.model.get_controller('Cost Center', 'Root - EW')
		self.assertRaises(webnotes.MandatoryError, account.validate)

	def test_group_to_ledger(self):
		# group with child can not be converted to ledger
		cc = webnotes.model.get_controller('Cost Center', 'Root - EW')
		self.assertRaises(webnotes.ValidationError, cc.convert_group_to_ledger)

		# successfull conversion (group to ledger)

		cc = webnotes.model.insert(base_cost_center)
		self.assertEqual(cc.convert_group_to_ledger(), 1)

	def test_ledger_to_group(self):
		# successfull conversion (ledger to group)
		cc = webnotes.model.insert(base_cost_center)
		self.assertEqual(cc.convert_ledger_to_group(), 1)

		# account with existing ledger entry can not be converted
		cc = base_cost_center.copy()
		cc.update({'cost_center_name': 'West'})
		cc = webnotes.model.insert(cc)

		webnotes.model.insert_variants(base_gle, [{'account': 'Sales - EW', 'cost_center': cc.doc['name']}])
		self.assertRaises(webnotes.ValidationError, cc.convert_ledger_to_group)

	def test_nsm_model(self):
		prev_rgt = self.get_rgt("Root - EW")
		webnotes.model.insert(base_cost_center)
		self.assertEqual(self.get_rgt("Root - EW"), prev_rgt + 2)
		self.assertNsm('Cost Center', 'parent_cost_center', 'group_or_ledger')

	def get_rgt(self, cc):
		return webnotes.conn.get_value("Cost Center", cc, "rgt")
		
	def test_cc_deletion(self):		
		# successfull deletion
		cc = webnotes.model.insert(base_cost_center)
		prev_rgt = self.get_rgt("Root - EW")
		webnotes.model.delete_doc('Cost Center', cc.doc.name)

		self.assertFalse(webnotes.conn.exists('Cost Center', 'test_cost_center - EW'))
		self.assertEqual(self.get_rgt("Root - EW"), prev_rgt - 2)
		self.assertNsm('Cost Center', 'parent_cost_center', 'group_or_ledger')

	def test_cc_renaming(self):
		# successfull renaming
		webnotes.model.insert(base_cost_center)

		from webnotes.model.rename_doc import rename_doc
		rename_doc("Cost Center", "test_cost_center - EW", "test_cost_center_renamed - EW")

		self.assertFalse(webnotes.conn.exists("Cost Center", "test_cost_center - EW"))
		self.assertTrue(webnotes.conn.exists("Cost Center", "test_cost_center_renamed - EW"))