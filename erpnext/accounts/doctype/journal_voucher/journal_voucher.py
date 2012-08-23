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
		if self.doc.docstatus == 0:
			self.get_total()
		
	def get_total(self):
		self.doc.total_debit, self.doc.total_credit = 0, 0
		for d in self.doclist.get({'parentfield': 'entries'}):
			self.doc.total_debit += flt(d.debit)
			self.doc.total_credit += flt(d.credit)
		
	def on_submit(self):
		from accounts.doctype.journal_voucher.gl_mapper import gl_mapper
		self.make_gl_entries(gl_mapper)
	
	def on_cancel(self):
		self.delete_gl_entries()
		
		
# TODO : 
#
#Against transaction validation to be implemented through DocType Validator
# party matching with sales/pur invoice/JV
# Against JV can not be same document