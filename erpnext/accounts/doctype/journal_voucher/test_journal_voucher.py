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

base_party = {
	'doctype': 'Party', 'name': 'test_party', 'party_type': 'Customer'
}

base_acc = [
	{'doctype': 'Account', 'account_name': 'Party Account', 'company': 'East Wind Corporation'},
	{'doctype': 'Account', 'account_name': 'Bank Account', 'company': 'East Wind Corporation'}
]

base_jv = {
	'doctype': 'Journal Voucher', 'naming_series': 'JV',
	'posting_date': '2012-04-01', 'company': 'East Wind Corporation'
}

class TestJournalVoucher(TestBase):
	def setUp(self):
		super(TestJournalVoucher).setUp()
		webnotes.model.insert(base_party)
		webnotes.model.insert(base_acc)
		
	def test_jv_creation(self):
		entry_line1 = {
			'doctype': 'Journal Voucher Detail', 'account_name': 'Party Account',
			'party': 'test_party', 'credit': 100
		}
		entry_line2 = {
			'doctype': 'Journal Voucher Detail', 'account_name': 'Bank Account',
			'debit': 100
		}
		webnotes.model.insert([base_jv, entry_line1, entry_line2])
		print webnotes.conn.get_value('Journal Voucher', \
			{'total_debit': 100, 'total_credit': 100})
		self.assertTrue(webnotes.conn.exists('Journal Voucher', \
			{'name': 'JV00001', 'total_debit': 100, 'total_credit': 100}))