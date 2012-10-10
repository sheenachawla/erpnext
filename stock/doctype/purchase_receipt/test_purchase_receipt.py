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

# Please edit this list and import only required elements

from __future__ import unicode_literals
import unittest
import webnotes
import webnotes.model
from webnotes.utils import nowdate, flt
from accounts.utils import get_fiscal_year

company = webnotes.conn.get_default("company")
abbr = webnotes.conn.get_value("Company", company, "abbr")

def load_data():
	# create default warehouse
	webnotes.model.insert({"doctype": "Warehouse", "warehouse_name": "Default Warehouse",
		"warehouse_type": "Stores"})
	
	# create UOM: Nos.
	webnotes.model.insert({"doctype": "UOM", "uom_name": "Nos"})
	
	from webnotes.tests import insert_test_data
	# create item groups and items
	insert_test_data("Item Group", 
		sort_fn=lambda ig: (ig[0].get('parent_item_group'), ig[0].get('name')))
	insert_test_data("Item")

	# create supplier type
	webnotes.model.insert({"doctype": "Supplier Type", "supplier_type": "Manufacturing"})
	
	# create supplier
	webnotes.model.insert({"doctype": "Supplier", "supplier_name": "North East Traders",
		"supplier_type": "Manufacturing", "company": company})


base_purchase_receipt = {"doctype": "Purchase Receipt", "supplier": "North East Traders",
	"naming_series": "PR", "posting_date": nowdate(), "posting_time": "12:05",
	"company": company, "fiscal_year": webnotes.conn.get_default("fiscal_year"), 
	"currency": webnotes.conn.get_default("currency"), "conversion_rate": 1
}

base_purchase_receipt_item = {"doctype": "Purchase Receipt Item", "item_code": "Home Desktop 100",
	"qty": 10, "received_qty": 10, "rejected_qty": 0, "purchase_rate": "10", 
	"amount": "100", "warehouse": "Default Warehouse", "parentfield": "purchase_receipt_details",
	"conversion_factor": 1, "uom": "Nos", "stock_uom": "Nos"}

class TestPurchaseReceipt(unittest.TestCase):
	def setUp(self):
		webnotes.conn.begin()
		load_data()
		
	def test_purchase_receipt(self):
		# warehouse does not have stock in hand specified
		self.run_purchase_receipt_test([base_purchase_receipt.copy(),
			base_purchase_receipt_item.copy()], 
			"Default Warehouse - Warehouse - %s" % (abbr,), 
			"Stock Received But Not Billed - %s" % (abbr,))
	
	def run_purchase_receipt_test(self, purchase_receipt, debit_account, credit_account):
		print len(purchase_receipt)
		dl = webnotes.model.insert(purchase_receipt)
		print len(dl.doclist)
		dl.submit()
		dl.load_from_db()
		print len(dl.doclist)
				
		gle = webnotes.conn.sql("""select account, ifnull(debit, 0), ifnull(credit, 0)
			from `tabGL Entry` where voucher_no = %s""", dl.doclist[0].name)
		print gle
		
		gle_map = dict(((entry[0], entry) for entry in gle))
		print gle_map.keys()
		
		self.assertEquals(gle_map[debit_account], (debit_account, 100.0, 0.0))
		self.assertEquals(gle_map[credit_account], (credit_account, 0.0, 100.0))
		
	def tearDown(self):
		webnotes.conn.rollback()