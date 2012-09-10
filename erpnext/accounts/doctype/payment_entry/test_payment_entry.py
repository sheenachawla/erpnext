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
from webnotes.model import get_controller

base_party = [
	{'doctype': 'Party', 'name': 'test_customer', 'party_type': 'Customer'},
	{'doctype': 'Party', 'name': 'test_supplier', 'party_type': 'Supplier'},
]

base_acc = [
	{
		"doctype": "Account", "account_name": "test_receivable",
		"parent_account": "Accounts Receivable - EW",
		"group_or_ledger": "Ledger", "debit_or_credit": "Debit",
		"is_pl_account": "No", "company": "East Wind Corporation"
	},
	{
		"doctype": "Account", "account_name": "test_payable",
		"parent_account": "Accounts Receivable - EW",
		"group_or_ledger": "Ledger", "debit_or_credit": "Credit",
		"is_pl_account": "No", "company": "East Wind Corporation"
	},
	{
		"doctype": "Account", "account_name": "test_bank",
		"parent_account": "Bank Accounts - EW",
		"group_or_ledger": "Ledger", "debit_or_credit": "Debit",
		"is_pl_account": "No", "company": "East Wind Corporation"
	}
]

base_payment_entry = {
	'doctype': 'Payment Entry', 'naming_series': 'PE',
	'posting_date': '2012-04-01', 'company': 'East Wind Corporation', 
	'__islocal': 1, 'send_or_receive': 'Receive', 'payment_amount': 100
}

class TestPaymentEntry(TestBase):
	def setUp(self):
		super(TestPaymentEntry, self).setUp()
		for party in base_party:
			webnotes.model.insert(party)
		for acc in base_acc:
			webnotes.model.insert(acc)
		
	def test_payment_from_customer(self):
		payment_entry = base_payment_entry.copy()
		payment_entry.update({
			'party': 'test_customer',
			'receivable_payable_account': 'test_receivable - EW',
			'bank_cash_account': 'test_bank - EW'
		})
		payment_ctlr = get_controller([payment_entry])
		#submit
		payment_ctlr.submit()
		#check gl entry record
		self.assertTrue(webnotes.conn.exists('GL Entry', {
			'account': 'test_bank - EW', 'debit': 100, 
			'posting_date': '2012-04-01', 'voucher_type': 'Payment Entry',
			'voucher_no': payment_ctlr.doc.name, 'company': 'East Wind Corporation'
		}))
		self.assertTrue(webnotes.conn.exists('GL Entry', {
			'account': 'test_receivable - EW', 'party': 'test_customer', 'credit': 100,
			'posting_date': '2012-04-01', 'voucher_type': 'Payment Entry',
			'voucher_no': payment_ctlr.doc.name, 'company': 'East Wind Corporation',
			'against_voucher_type[""]': "", 'against_voucher[""]': ""
		}))
		#cancel
		payment_ctlr.cancel()
		# no gl entry
		self.assertFalse(webnotes.conn.exists('GL Entry', {
			'voucher_type': 'Payment Entry', 'voucher_no': 'PE00001'
		}))
		
	def test_payment_to_customer(self):
		payment_entry = base_payment_entry.copy()
		payment_entry.update({
			'party': 'test_customer',
			'receivable_payable_account': 'test_receivable - EW',
			'bank_cash_account': 'test_bank - EW',
			'send_or_receive': 'Send'
		})
		payment_ctlr = get_controller([payment_entry])
		#submit
		payment_ctlr.submit()
		#check gl entry record
		self.assertTrue(webnotes.conn.exists('GL Entry', {
			'account': 'test_bank - EW', 'credit': 100, 
			'posting_date': '2012-04-01', 'voucher_type': 'Payment Entry',
			'voucher_no': payment_ctlr.doc.name, 'company': 'East Wind Corporation'
		}))
		self.assertTrue(webnotes.conn.exists('GL Entry', {
			'account': 'test_receivable - EW', 'party': 'test_customer', 'debit': 100,
			'posting_date': '2012-04-01', 'voucher_type': 'Payment Entry',
			'voucher_no': payment_ctlr.doc.name, 'company': 'East Wind Corporation',
			'against_voucher_type[""]': "", 'against_voucher[""]': ""
		}))
		#cancel
		payment_ctlr.cancel()
		# no gl entry
		self.assertFalse(webnotes.conn.exists('GL Entry', {
			'voucher_type': 'Payment Entry', 'voucher_no': 'PE00001'
		}))
		
	def test_payment_to_supplier(self):
		payment_entry = base_payment_entry.copy()
		payment_entry.update({
			'party': 'test_supplier',
			'receivable_payable_account': 'test_payable - EW',
			'bank_cash_account': 'test_bank - EW',
			'send_or_receive': 'Send'
		})
		payment_ctlr = get_controller([payment_entry])
		#submit
		payment_ctlr.submit()
		#check gl entry record
		self.assertTrue(webnotes.conn.exists('GL Entry', {
			'account': 'test_bank - EW', 'credit': 100, 
			'posting_date': '2012-04-01', 'voucher_type': 'Payment Entry',
			'voucher_no': payment_ctlr.doc.name, 'company': 'East Wind Corporation'
		}))
		self.assertTrue(webnotes.conn.exists('GL Entry', {
			'account': 'test_payable - EW', 'party': 'test_supplier', 'debit': 100,
			'posting_date': '2012-04-01', 'voucher_type': 'Payment Entry',
			'voucher_no': payment_ctlr.doc.name, 'company': 'East Wind Corporation',
			'against_voucher_type[""]': "", 'against_voucher[""]': ""
		}))
		#cancel
		payment_ctlr.cancel()
		# no gl entry
		self.assertFalse(webnotes.conn.exists('GL Entry', {
			'voucher_type': 'Payment Entry', 'voucher_no': 'PE00001'
		}))
	
	def test_payment_from_supplier(self):
		payment_entry = base_payment_entry.copy()
		payment_entry.update({
			'party': 'test_supplier',
			'receivable_payable_account': 'test_payable - EW',
			'bank_cash_account': 'test_bank - EW',
			'send_or_receive': 'Receive'
		})
		payment_ctlr = get_controller([payment_entry])
		#submit
		payment_ctlr.submit()
		#check gl entry record
		self.assertTrue(webnotes.conn.exists('GL Entry', {
			'account': 'test_bank - EW', 'debit': 100, 
			'posting_date': '2012-04-01', 'voucher_type': 'Payment Entry',
			'voucher_no': payment_ctlr.doc.name, 'company': 'East Wind Corporation'
		}))
		self.assertTrue(webnotes.conn.exists('GL Entry', {
			'account': 'test_payable - EW', 'party': 'test_supplier', 'credit': 100,
			'posting_date': '2012-04-01', 'voucher_type': 'Payment Entry',
			'voucher_no': payment_ctlr.doc.name, 'company': 'East Wind Corporation',
			'against_voucher_type[""]': "", 'against_voucher[""]': ""
		}))
		#cancel
		payment_ctlr.cancel()
		# no gl entry
		self.assertFalse(webnotes.conn.exists('GL Entry', {
			'voucher_type': 'Payment Entry', 'voucher_no': 'PE00001'
		}))
				
	def test_payment_from_party_against_invoice(self):
		"""to be implemented after sales/purchase invoice rewrite"""
		pass
		
	def test_negative_debit_credit(self):
		payment_entry = base_payment_entry.copy()
		payment_entry.update({
			'party': 'test_customer',
			'receivable_payable_account': 'test_receivable - EW',
			'bank_cash_account': 'test_bank - EW',
			'payment_amount': -100
		})
		payment_ctlr = get_controller([payment_entry])
		payment_ctlr.submit()
		
		self.assertTrue(webnotes.conn.exists('GL Entry', {
			'account': 'test_bank - EW', 'credit': 100, 
			'posting_date': '2012-04-01', 'voucher_type': 'Payment Entry',
			'voucher_no': payment_ctlr.doc.name, 'company': 'East Wind Corporation'
		}))
		
	def test_if_sales_purchase_invoice_both(self):
		"""to be implemented after sales/purchase invoice rewrite"""
		pass