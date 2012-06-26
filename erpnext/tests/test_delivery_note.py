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
	
	
	def test_over_delivery_validation(self):
		print "Testcase: DN submission failed due to over-delivery"

		from selling.doctype.sales_common.sales_common import OverDeliveryError		
		# create and submit so
		self.submit_doc(so_data, on_update=1)
		
		# check over delivery validation on submission of DN
		self.assertRaises(OverDeliveryError, self.submit_doc, (dn_over_delivery))

		
	def test_over_delivery_submit(self):
		print "Testcase: Over Delivery submission - check actual qty, reserved qty, stock ledger entries"
		
		# create and submit so
		self.submit_doc(so_data, on_update=1)
		# create material receipt for initial stock
		self.submit_doc(mr_data, on_update=1)		
		# change global tolerance
		webnotes.conn.set_value('Global Defaults', None, 'tolerance', 20)
		#submit dn
		self.submit_doc(dn_over_delivery)
		
		# bin reserved qty - wh1
		self.assertDoc([{'doctype':'Bin', 'reserved_qty':0, 'item_code':'test_item', 'warehouse':'test_wh1'}])		
		# bin actual qty - wh2
		self.assertDoc([{'doctype':'Bin', 'reserved_qty':0, 'actual_qty': 8, 'item_code':'test_item', 'warehouse':'test_wh2'}])
		
	def test_over_delivery_cancel(self):
		print "Testcase: Over Delivery cancellation - check actual qty, reserved qty, stock ledger entries"

		# create and submit so
		self.submit_doc(so_data, on_update=1)
		# create material receipt for initial stock
		self.submit_doc(mr_data, on_update=1)
		# change global tolerance
		webnotes.conn.set_value('Global Defaults', None, 'tolerance', 20)
		#cancel dn
		self.cancel_doc(dn_over_delivery)

		# bin reserved qty - wh1
		self.assertDoc([{'doctype':'Bin', 'reserved_qty':10, 'item_code':'test_item', 'warehouse':'test_wh1'}])		
		# bin actual qty - wh2
		self.assertDoc([{'doctype':'Bin', 'reserved_qty':0, 'actual_qty': 20, 'item_code':'test_item', 'warehouse':'test_wh2'}])
		
		
	def test_negative_stock_validation(self):
		print "Test Case: Item is out of stock - validation check"
				
		from stock.doctype.bin.bin import NegativeStockError
		self.assertRaises(NegativeStockError, self.submit_doc, dn_part_delivery, on_update=1)
		
		
	def test_allow_negative_stock(self):
		print "Test case: Negative stock allowed"
		
		webnotes.conn.set_default('allow_negative_stock', 1)
		webnotes.conn.set_default('valuation_method', 'Moving Average')
		self.submit_doc(dn_part_delivery, on_update=1)
		
		# check bin qty
		self.assertDoc([{'doctype':'Bin', 'actual_qty': -4, 'item_code':'test_item', 'warehouse':'test_wh2'}])
		
	
	def test_part_delivery_submit(self):
		print "TestCase: Succesfull submission of part delivery"
		
		# create material receipt for initial stock
		self.submit_doc(mr_data, on_update=1)
		#submit dn
		self.submit_doc(dn_part_delivery, on_update=1)
				
		# bin actual qty - wh2
		self.assertDoc([{'doctype':'Bin', 'reserved_qty':0, 'actual_qty': 16, 'item_code':'test_item', 'warehouse':'test_wh2'}])
		

	def test_part_delivery_cancel(self):
		print "TestCase: Succesfull cancellation of part delivery"

		# create material receipt for initial stock
		self.submit_doc(mr_data, on_update=1)
		#submit dn
		self.cancel_doc(dn_part_delivery, on_update=1)

		# bin actual qty - wh2
		self.assertDoc([{'doctype':'Bin', 'reserved_qty':0, 'actual_qty': 20, 'item_code':'test_item', 'warehouse':'test_wh2'}])
	
	
# Test Data
so_data = [
	{'doctype': 'Sales Order', 'name': 'SO001', 'customer': 'test_customer', 'transaction_date': '2012-06-25'},
	{'doctype': 'Sales Order Item', 'name': 'SOD00001', 'parent': 'SO001', 'parentfield': 'sales_order_details', \
	'parenttype': 'Sales Order', 'item_code': 'test_item', 'qty': 10, 'stock_uom': 'Nos', 'basic_rate': 100, \
	'amount': 1000, 'reserved_warehouse': 'test_wh1'}
]

dn_over_delivery = [
	{'doctype': 'Delivery Note', 'name': 'DN001', 'customer': 'test_customer', 'posting_date': '2012-06-26',\
	 'company': 'Test Company', 'fiscal_year': '2012-2013', 'posting_time': '12:05', 'net_total': 1200, 'grand_total': 1200},
	{'doctype': 'Delivery Note Item', 'name': 'DND00001', 'parent': 'DN001', 'parentfield': 'delivery_note_details', \
	'parenttype': 'Delivery Note', 'item_code': 'test_item', 'qty': 12, 'stock_uom': 'Nos', 'basic_rate': 100, \
	'amount': 1200, 'warehouse': 'test_wh2', 'prevdoc_docname': 'SO001', 'prevdoc_doctype': 'Sales Order', \
	'prevdoc_detail_docname': 'SOD00001'}
]

dn_part_delivery = [
	{'doctype': 'Delivery Note', 'name': 'DN001', 'customer': 'test_customer', 'posting_date': '2012-06-26',\
	 'company': 'Test Company', 'fiscal_year': '2012-2013', 'posting_time': '12:05', 'net_total': 400, 'grand_total': 400},
	{'doctype': 'Delivery Note Item', 'name': 'DND00001', 'parent': 'DN001', 'parentfield': 'delivery_note_details', \
	'parenttype': 'Delivery Note', 'item_code': 'test_item', 'qty': 4, 'stock_uom': 'Nos', 'basic_rate': 100, \
	'amount': 400, 'warehouse': 'test_wh2', 'prevdoc_docname': 'SO001', 'prevdoc_doctype': 'Sales Order', \
	'prevdoc_detail_docname': 'SOD00001'}
]

mr_data =[
	{'doctype': 'Stock Entry', 'posting_date': '2012-06-20', 'transfer_date': '2012-06-20', 'posting_time': '12:00',\
	'company': 'Test Company', 'fiscal_year' : '2012-2013', 'purpose': 'Material Receipt', 'name': 'MR001'},
	{'doctype': 'Stock Entry Detail', 'parenttype': 'Stock Entry', 'parentfield' : 'mtn_details', 'parent' : 'MR001',\
	'item_code' : 'test_item', 't_warehouse' : 'test_wh2', 'qty' : 20, 'incoming_rate': 100, 'stock_uom': 'Nos', \
	'transfer_qty' : 20, 'name': 'SED0001'}
]


if __name__ == '__main__':
	unittest.main()