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
from accounts.utils import GLController


class PaymentEntryController(GLController):
	def validate(self):
		if self.doc.sales_invoice and self.doc.purchase_invoice:
			webnotes.msgprint("You can enter either Sales Invoice or Purchase Invoice"
				, raise_exception=webnotes.ValidationError)
		
	def on_submit(self):
		from accounts.doctype.payment_entry.gl_mapper import gl_mapper
		self.make_gl_entries(gl_mapper)
	
	def on_cancel(self):
		self.delete_gl_entries()