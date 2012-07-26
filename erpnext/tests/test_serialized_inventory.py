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
import unittest
import sys
sys.path.append('lib/py')
sys.path.append('erpnext')

import webnotes


from testdata.masters import masters
from testdata.stock_entry import *
from utils import TestBase

class TestSerializedInventory(TestBase):
	def setUp(self):
		TestBase.setUp(self)
		self.create_docs(masters, validate=1, on_update=1)	

	def test_direct_serial_no_creation(self):
		pass
		
	def test_serial_no_deletion(self):
		pass
		
	def test_pur_receipt_submit(self):
		pass
	
	def test_pur_receipt_cancel(self):
		pass

	def test_delivery_note_submit(self):
		pass

	def test_delivery_note_cancel(self):
		pass
		
	def test_khichdi(self):
		pass
		
	def test_mr_onsubmit(self):
		print "Test Case: Material Receipt submission"
		self.submit_doc(mr, 1, 1)

		# stock ledger entry
		self.assertDoc(self.get_expected_sle('mr_submit'))
		# bin qty
		self.assertDoc([{'doctype':'Bin', 'actual_qty':10, 'item_code':'test_item_serialized', 'warehouse':'test_wh1'}])
		# serial no
		self.assertCount([[{'doctype': 'Serial No', 'item_code': 'test_item_serialized', 'warehouse': 'test_wh1', 'status': 'In Store', 'docstatus': 0}, 10]])


	def test_mr_oncancel(self):
		print "Test Case: Material Receipt Cancellation"
		self.cancel_doc(mr, 1, 1)

		# stock ledger entry
		self.assertDoc(self.get_expected_sle('mr_cancel'))
		# bin qty
		self.assertDoc([{'doctype':'Bin', 'actual_qty':0, 'item_code':'test_item_serialized', 'warehouse':'test_wh1'}])
		# serial no
		self.assertCount([[{'doctype': 'Serial No', 'item_code': 'test_item_serialized', 'warehouse': '', 'status': 'Not in Use', 'docstatus': 2}, 10]])


	def test_mtn_onsubmit(self):
		print "Test Case: Material Transfer Note submission"
		self.submit_doc(mr, 1, 1)
		self.submit_doc(mtn, 1, 1)

		# stock ledger entry
		self.assertDoc(self.get_expected_sle('mtn_submit'))
		# bin qty
		self.assertDoc([
			{'doctype':'Bin', 'actual_qty':5, 'item_code':'test_item_serialized', 'warehouse':'test_wh1'},
			{'doctype':'Bin', 'actual_qty':5, 'item_code':'test_item_serialized', 'warehouse':'test_wh2'}
		])
		# serial no		
		self.assertCount([
			[{'doctype': 'Serial No', 'item_code': 'test_item_serialized', 'warehouse': 'test_wh1', 'status': 'In Store', 'docstatus': 0}, 5], 
			[{'doctype': 'Serial No', 'item_code': 'test_item_serialized', 'warehouse': 'test_wh2', 'status': 'In Store', 'docstatus': 0}, 5]
		])


	def test_mtn_oncancel(self):
		print "Test Case: Material Transfer Note Cancellation"
		self.submit_doc(mr, 1, 1)
		self.cancel_doc(mtn, 1, 1)

		# stock ledger entry
		self.assertDoc(self.get_expected_sle('mtn_cancel'))
		# bin qty
		self.assertDoc([
			{'doctype':'Bin', 'actual_qty':10, 'item_code':'test_item_serialized', 'warehouse':'test_wh1'},
			{'doctype':'Bin', 'actual_qty':0, 'item_code':'test_item_serialized', 'warehouse':'test_wh2'}
		])
		# serial no
		self.assertCount([[{'doctype': 'Serial No', 'item_code': 'test_item_serialized', 'warehouse': 'test_wh1', 'status': 'In Store', 'docstatus': 0}, 10]])


	def test_mi_onsubmit(self):
		print "Test Case: Material Issue submission"
		self.submit_doc(mr, 1, 1)
		self.submit_doc(mi, 1, 1)

		# stock ledger entry
		self.assertDoc(self.get_expected_sle('mi_submit'))
		# bin qty
		self.assertDoc([{'doctype':'Bin', 'actual_qty':6, 'item_code':'test_item_serialized', 'warehouse':'test_wh1'}])
		# serial no		
		self.assertCount([
			[{'doctype': 'Serial No', 'item_code': 'test_item_serialized', 'warehouse': 'test_wh1', 'status': 'In Store', 'docstatus': 0}, 6]
		])


	def test_mi_oncancel(self):
		print "Test Case: Material Issue Cancellation"
		self.submit_doc(mr, 1, 1)
		self.cancel_doc(mi, 1, 1)

		# stock ledger entry
		self.assertDoc(self.get_expected_sle('mi_cancel'))
		# bin qty
		self.assertDoc([
			{'doctype':'Bin', 'actual_qty':10, 'item_code':'test_item_serialized', 'warehouse':'test_wh1'}
		])
		# serial no
		self.assertCount([
			[{'doctype': 'Serial No', 'item_code': 'test_item_serialized', 'warehouse': 'test_wh1', 'status': 'In Store', 'docstatus': 0}, 10]
		])

	def test_entries_on_same_datetime(self):
		print "Test Case: Multiple entries on same datetime, cancel first one"
		m = self.submit_doc(mr, 1, 1)

		self.submit_doc(mr1, 1, 1)
		self.submit_doc(mtn, 1, 1)

		# cancel 1st MR
		m.on_cancel()
		m.doc.cancel_reason = "testing"
		m.doc.docstatus = 2
		m.doc.save()

		# stock ledger entry
		self.assertDoc(self.get_expected_sle('entries_on_same_datetime'))
		# bin qty
		self.assertDoc([
			{'doctype':'Bin', 'actual_qty':0, 'item_code':'test_item_serialized', 'warehouse':'test_wh1'},
			{'doctype':'Bin', 'actual_qty':5, 'item_code':'test_item_serialized', 'warehouse':'test_wh2'}
		])
		# serial no		
		self.assertCount([
			[{'doctype': 'Serial No', 'item_code': 'test_item_serialized', 'warehouse': 'test_wh1', 'status': 'In Store', 'docstatus': 0}, 5], 
			[{'doctype': 'Serial No', 'item_code': 'test_item_serialized', 'warehouse': 'test_wh2', 'status': 'In Store', 'docstatus': 0}, 0]
		])


	# Expected Result Set (Stock ledger entry)
	#===================================================================================================
	def get_expected_sle(self, action):
		expected_sle = {
			'mr_submit': [{
							'doctype': 'Stock Ledger Entry',
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1', 
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MR001',
							'actual_qty': 10,
							'bin_aqat': 10,
							'valuation_rate': 100,
							'is_cancelled': 'No'
						}],
			'mr_cancel': [{
							'doctype': 'Stock Ledger Entry', 
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MR001',
							'actual_qty': 10,
							'bin_aqat': 10,
							'valuation_rate': 100,
							'is_cancelled': 'Yes'
						},{
							'doctype': 'Stock Ledger Entry', 
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MR001',
							'actual_qty': -10,
							'ifnull(bin_aqat, 0)': 0,
							'ifnull(valuation_rate, 0)': 0,
							"ifnull(is_cancelled, 'No')": 'Yes'
						}],
			'mtn_submit': [{
							'doctype': 'Stock Ledger Entry',
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MTN001',
							'actual_qty': -5,
							'bin_aqat': 5,
							'valuation_rate': 100,
							'is_cancelled': 'No'
						}, {
							'doctype': 'Stock Ledger Entry',
							'item_code':'test_item_serialized',
							'warehouse':'test_wh2',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MTN001',
							'actual_qty': 5,
							'bin_aqat': 5,
							'valuation_rate': 100,
							'is_cancelled': 'No'
						}],
			'mtn_cancel': [{
							'doctype': 'Stock Ledger Entry',
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MTN001',
							'actual_qty': -5,
							'bin_aqat': 5,
							'is_cancelled': 'Yes'
						}, {
							'doctype': 'Stock Ledger Entry',
							'item_code':'test_item_serialized',
							'warehouse':'test_wh2',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MTN001',
							'actual_qty': 5,
							'bin_aqat': 5,
							'valuation_rate': 100,
							'is_cancelled': 'Yes'
						}, {
							'doctype': 'Stock Ledger Entry',
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MTN001',
							'actual_qty': 5,
							'is_cancelled': 'Yes'
						}, {
							'doctype': 'Stock Ledger Entry',
							'item_code':'test_item_serialized',
							'warehouse':'test_wh2',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MTN001',
							'actual_qty': -5,
							'is_cancelled': 'Yes'
						}],
			'mi_submit': [{'doctype': 'Stock Ledger Entry',
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1', 
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MI001',
							'actual_qty': -4,
							'bin_aqat': 6,
							'valuation_rate': 100,
							'is_cancelled': 'No'
						}],
			'mi_cancel': [{
							'doctype': 'Stock Ledger Entry', 
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MI001',
							'actual_qty': -4,
							'bin_aqat': 6,
							'valuation_rate': 100,
							'is_cancelled': 'Yes'
						},{
							'doctype': 'Stock Ledger Entry', 
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MI001',
							'actual_qty': 4,
							'ifnull(bin_aqat, 0)': 0,
							'ifnull(valuation_rate, 0)': 0,
							"ifnull(is_cancelled, 'No')": 'Yes'
						}],
			'entries_on_same_datetime': [{
							'doctype': 'Stock Ledger Entry', 
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MR001',
							'actual_qty': 10,
							'bin_aqat': 10,
							'valuation_rate': 100,
							'is_cancelled': 'Yes'
						}, {
							'doctype': 'Stock Ledger Entry', 
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MR001',
							'actual_qty': -10,
							'ifnull(bin_aqat, 0)': 0,
							'ifnull(valuation_rate, 0)': 0,
							"ifnull(is_cancelled, 'No')": 'Yes'
						}, {
							'doctype': 'Stock Ledger Entry', 
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MR002',
							'actual_qty': 5,
							'bin_aqat': 5,
							'valuation_rate': 400,
							'is_cancelled': 'No'
						}, {
							'doctype': 'Stock Ledger Entry',
							'item_code':'test_item_serialized',
							'warehouse':'test_wh1',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MTN001',
							'actual_qty': -5,
							'bin_aqat': 0,
							'valuation_rate': 400,
							'is_cancelled': 'No'
						}, {
							'doctype': 'Stock Ledger Entry',
							'item_code':'test_item_serialized',
							'warehouse':'test_wh2',
							'voucher_type': 'Stock Entry',
							'voucher_no': 'MTN001',
							'actual_qty': 5,
							'bin_aqat': 5,
							'valuation_rate': 100,
							'is_cancelled': 'No'
						}]
		}

		return expected_sle[action]

# Data
#----------
sr = [
	{'doctype': 'Serial No', 'name': 'sr001', 'item_code': 'test_item_serialized', 'warehouse': 'testwh1', \
	'incoming_rate': 100, 'status': 'In Store'},
	{'doctype': 'Serial No', 'name': 'sr002', 'item_code': 'test_item_serialized', 'warehouse': 'testwh1', \
	'incoming_rate': 100, 'status': 'Delivered'},
	{'doctype': 'Serial No', 'name': 'sr002', 'item_code': 'test_item_serialized', 'warehouse': 'testwh1', \
	'incoming_rate': 100, 'status': 'Not in Use'},
	
]
		
if __name__ == '__main__':
	unittest.main()