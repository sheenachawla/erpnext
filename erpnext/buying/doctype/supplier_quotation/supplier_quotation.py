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

from controllers.buying import BuyingController
class SupplierQuotationController(BuyingController):
	def setup(self):
		self.item_table_fieldname = 'supplier_quotation_items'
	
	def validate(self):
		if self.doc.docstatus != 2:
			# validate for draft, submit
			super(SupplierQuotationController, self).validate_items(
				"supplier_quotation_items")
			super(SupplierQuotationController, self).validate_previous_doclist(
				"purchase_request", "purchase_request_item")
			# TODO: validate reference values
		else:
			# validate for cancel
			pass
