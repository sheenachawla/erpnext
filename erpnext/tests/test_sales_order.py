import unittest, sys
sys.path.append('lib/py')
sys.path.append('erpnext')

import webnotes
from webnotes.utils import cstr, cint, flt

from testdata.masters import masters
from utils import TestBase

class TestMasters(TestBase):
	def setUp(self):
		TestBase.setUp(self)
		self.create_docs(masters, validate=1, on_update=1)
		print 'Master Data Created'
	

	def test_reserved_qty_onsubmit(self):
		print "TesCase: Reserved qty check on submission of SO"
		self.submit_doc(so_data, on_update=1)
		self.assertDoc([{'doctype':'Bin', 'reserved_qty':10, 'item_code':'test_item', 'warehouse':'test_wh1'}])
		
	def test_reserved_qty_oncancel(self):
		print "TesCase: Reserved qty check on cancellation of SO"
		self.cancel_doc(so_data, on_update=1)
		self.assertDoc([{'doctype':'Bin', 'reserved_qty':0, 'item_code':'test_item', 'warehouse':'test_wh1'}])

# Test Data
so_data = [
	{'doctype': 'Sales Order', 'name': 'SO001', 'customer': 'test_customer', 'transaction_date': '2012-06-25'},
	{'doctype': 'Sales Order Item', 'name': 'SOD00001', 'parent': 'SO001', 'parentfield': 'sales_order_details', \
	'parenttype': 'Sales Order', 'item_code': 'test_item', 'qty': 10, 'stock_uom': 'Nos', 'basic_rate': 100, \
	'amount': 1000, 'reserved_warehouse': 'test_wh1'}
]


if __name__ == '__main__':
	unittest.main()