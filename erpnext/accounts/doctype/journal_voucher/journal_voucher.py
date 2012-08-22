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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.	If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
import webnotes
from webnotes.utils import flt
from accounts.utils import GLController

class JournalVoucherController(GLController):
	def validate(self):
		self.get_total()
		self.manage_opening_entry()
		
	def get_total(self):
		self.doc.total_debit, self.doc.total_credit = 0, 0
		for d in self.doclist.get({'parentfield': 'entries'}):
			self.doc.total_debit += flt(d.debit)
			self.doc.total_credit += flt(d.credit)
		
	def manage_opening_entry(self):
		if not self.doc.is_opening:
			self.doc.is_opening='No'
		self.doc.aging_date = self.doc.posting_date

	def on_submit(self):
		from accounts.doctype.journal_voucher.gl_mapper import jv_gle
		self.make_gl_entries(jv_gle)
	
	def on_cancel(self):
		self.delete_gl_entries()
		
		
# TODO : 
#
#Against transaction validation to be implemented through DocType Validator
# party matching with sales/pur invoice/JV
# Against JV can not be same document