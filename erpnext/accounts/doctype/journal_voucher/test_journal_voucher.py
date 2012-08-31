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
from webnotes.model import get_controller

base_party = {
	'doctype': 'Party', 'name': 'test_party', 'party_type': 'Customer'
}

base_acc = [
	{
		"doctype": "Account", "account_name": "test_party_account",
		"parent_account": "Accounts Receivable - EW",
		"group_or_ledger": "Ledger", "debit_or_credit": "Debit",
		"is_pl_account": "No", "company": "East Wind Corporation"
	},
	{
		"doctype": "Account", "account_name": "test_bank_account",
		"parent_account": "Bank Accounts - EW",
		"group_or_ledger": "Ledger", "debit_or_credit": "Debit",
		"is_pl_account": "No", "company": "East Wind Corporation"
	}
]

class TestJournalVoucher(TestBase):
	def setUp(self):
		super(TestJournalVoucher, self).setUp()
		webnotes.model.insert(base_party)
		for acc in base_acc:
			webnotes.model.insert(acc)
			
	def get_base_jv(self):
		jv = [
			{
				'doctype': 'Journal Voucher', 'naming_series': 'JV',
				'posting_date': '2012-04-01', 'company': 'East Wind Corporation', '__islocal': 1
			},
			{
				'doctype': 'Journal Voucher Detail', 'account': 'test_party_account - EW',
				'party': 'test_party', 'credit': 100, 'parentfield': 'entries', '__islocal': 1
			},
			{
				'doctype': 'Journal Voucher Detail', 'account': 'test_bank_account - EW',
				'debit': 100, 'parentfield': 'entries', '__islocal': 1
			}
		]
		return jv
				
	def test_jv_creation(self):
		webnotes.model.insert(self.get_base_jv())
		self.assertTrue(webnotes.conn.exists('Journal Voucher', 'JV00001'))
		
	def test_jv_submission(self):
		jv = self.get_base_jv()
		jv[0]['docstatus'] = 1
		webnotes.model.insert(jv)
		
		#check gl entry record
		self.assertTrue(webnotes.conn.exists('GL Entry', {
			'account': 'test_bank_account - EW', 'debit': 100, 
			'posting_date': '2012-04-01', 'voucher_type': 'Journal Voucher',
			'voucher_no': 'JV00001', 'company': 'East Wind Corporation'
		}))
		self.assertTrue(webnotes.conn.exists('GL Entry', {
			'account': 'test_party_account - EW', 'party': 'test_party', 'credit': 100,
			'posting_date': '2012-04-01', 'voucher_type': 'Journal Voucher',
			'voucher_no': 'JV00001', 'company': 'East Wind Corporation'
		}))
		
	def test_jv_cancellation(self):
		jv_ctlr = get_controller(self.get_base_jv())
		jv_ctlr.submit()
		jv_ctlr.cancel()
		# no gl entry
		self.assertFalse(webnotes.conn.exists('GL Entry', {
			'voucher_type': 'Journal Voucher', 'voucher_no': 'JV00001'
		}))
	
	def test_debit_equals_credit(self):
		jv = self.get_base_jv()
		jv[1].update({'credit': 200})
		self.assertRaises(webnotes.ValidationError, get_controller(jv).submit)
		
		
	def test_negative_debit_credit(self):
		jv = self.get_base_jv()
		jv[1].update({'credit': -100})
		jv[2].update({'debit': -100})
		get_controller(jv).submit()
		
		self.assertTrue(webnotes.conn.exists('GL Entry', {
			'account': 'test_bank_account - EW', 'credit': 100, 
			'posting_date': '2012-04-01', 'voucher_type': 'Journal Voucher',
			'voucher_no': 'JV00001', 'company': 'East Wind Corporation'
		}))