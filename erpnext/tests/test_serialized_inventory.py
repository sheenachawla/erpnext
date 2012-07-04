import unittest, sys
sys.path.append('lib/py')
sys.path.append('erpnext')

import webnotes
from webnotes.utils import cstr, cint, flt

from testdata.masters import masters
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