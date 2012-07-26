from __future__ import unicode_literals
import unittest
import sys
sys.path.append('lib/py')
sys.path.append('erpnext')

import webnotes
from webnotes.utils import cstr, cint, flt
from webnotes.model.code import get_obj

from testdata.masters import masters
from utils import TestBase

class TestMasters(TestBase):
	def setUp(self):
		TestBase.setUp(self)
		self.create_docs(masters, validate=1, on_update=1)
		print 'Master Data Created'
		
			
	def test_all_masters_with_tree_structure(self):
		print "NSM model test for account, cost center, customer group, item group and territory"
		self.assertNsm('Customer Group', 'parent_customer_group', 'is_group')
		self.assertNsm('Item Group', 'parent_item_group', 'is_group')
		self.assertNsm('Territory', 'parent_territory', 'is_group')
		self.assertNsm('Account', 'parent_account', 'group_or_ledger')
		self.assertNsm('Cost Center', 'parent_cost_center', 'group_or_ledger')
		
		
	def test_cust_supp_account(self):
		print "testing whether account created for customer"
		self.assertTrue(webnotes.conn.sql("select name from `tabAccount` where master_type = 'Customer' and master_name = 'test_customer'"))
		self.assertTrue(webnotes.conn.sql("select name from `tabAccount` where master_type = 'Supplier' and master_name = 'test_supplier'"))
		
	def test_account_change_parent(self):
		print "checking change parent function for account"
		
		
	def test_account_deletion(self):
		print "Checking account deletion"
		
		
	def test_account_group_to_ledger(self):
		print "checking change in group to ledger functionality"

	def test_customer_deletion(self):
		print "checking customer deletion, account should also be deleted"
			
		
if __name__ == '__main__':
	unittest.main()