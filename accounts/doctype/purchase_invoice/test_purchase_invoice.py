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

from stock.doctype.purchase_receipt import test_purchase_receipt

company = webnotes.conn.get_default("company")
abbr = webnotes.conn.get_value("Company", company, "abbr")

def load_data():
	test_purchase_receipt.load_data()
	
base_purchase_invoice = {"doctype": "Purchase Invoice", 
	"credit_to": "East Wind Inc. - %s" % abbr,
	"naming_series": "BILL", "posting_date": nowdate(),
	"company": company, "fiscal_year": webnotes.conn.get_default("fiscal_year"), 
	"currency": webnotes.conn.get_default("currency"), "conversion_rate": 1
}

base_purchase_invoice_item = {"doctype": "Purchase Invoice Item", 
	"item_code": "Home Desktop 100", "qty": 10, "rate": 50, 
	"amount": 500, "item_tax_amount": 250,
	"parentfield": "entries", "conversion_factor": 1, "uom": "Nos", "stock_uom": "Nos"}

class TestPurchaseReceipt(unittest.TestCase):
	def setUp(self):
		webnotes.conn.begin()
		load_data()
		
	def test_purchase_invoice(self):
		dl = webnotes.model.insert([
			base_purchase_invoice.copy(), base_purchase_invoice_item.copy(),
			test_purchase_receipt.shipping_charges.copy(),
			test_purchase_receipt.vat.copy(), test_purchase_receipt.customs_duty.copy()
		])		
		dl.submit()
		dl.load_from_db()
						
		# gle = webnotes.conn.sql("""select account, ifnull(debit, 0), ifnull(credit, 0)
		# 	from `tabGL Entry` where voucher_no = %s""", dl.doclist[0].name)
		# 
		# gle_map = dict(((entry[0], entry) for entry in gle))
		# 
		# self.assertEquals(gle_map[debit_account], (debit_account, 750.0, 0.0))
		# self.assertEquals(gle_map[credit_account], (credit_account, 0.0, 750.0))
		
	def tearDown(self):
		webnotes.conn.rollback()