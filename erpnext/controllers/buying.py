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

from webnotes.model.controller import DocListController
class BuyingController(DocListController):
	def validate_items(self, parentfield):
		for child in self.doclist.get({"parentfield": parentfield}):
			# get item controller. Also raises error if item not found
			itemdoc = webnotes.model.get("Item", child.item_code)[0]
			
			# check if purchase item
			if itemdoc.is_purchase_item != "Yes":
				webnotes.msgprint("""Item "%s" is not a Purchase Item""", raise_exception=True)

			# check if end of life has reached
			if itemdoc.end_of_life and getdate(itemdoc.end_of_life) <= \
					now_datetime().date():
				import stock
				webnotes.msgprint("""Item "%s" has reached its end of life""",
					raise_exception=stock.ItemEndOfLifeError)

			# check if warehouse is required
			# if itemdoc.is_stock_item == "Yes" and not child.warehouse:
			# 	webnotes.msgprint("""Warehouse is Mandatory for Item "%s", 
			# 		as it is a Stock Item""" % \
			# 		child.item_code, raise_exception=webnotes.MandatoryError)
			
	def validate_previous_doclist(self, parentfield, fieldname, item_fieldname):
		"""Validates current item row against previous item row"""
		doctypelist = webnotes.model.get_doctype(self.doc.doctype)
		prev_doctype = doctypelist.get_field(fieldname, parentfield=parentfield).options
		
		prev_doclist_cache = {}
		def get_prev_doclist(name):
			if not prev_doclist_cache.get(name):
				prev_doclist_cache[name] = webnotes.model.get(prev_doctype, name)
			return prev_doclist_cache.get(name)
		
		def errmsg(errfield, item, prev_item):
			label = doctypelist.get_label(errfield, parent=item.doctype)
			webnotes.msgprint("""%s of row # %d in the %s table
				cannot be different from the one in row # %d in the %s table 
				of %s: "%s" """ % (label, item.idx, item.doctype, prev_item.idx, 
				prev_item.doctype, prev_doctype, item.get(fieldname)),
				raise_exception=True)
		
		for item in self.doclist.get({"parentfield": parentfield}):
			if item.get(fieldname):
				prev_item = get_prev_doclist(item.get(fieldname)).getone({
					"name": item.get(item_fieldname)})
				
				if item.item_code != prev_item.item_code:
					# mismatch in item code
					errmsg("item_code", item, prev_item)
				if item.warehouse != prev_item.warehouse:
					# mismatch in warehouse
					errmsg("warehouse", item, prev_item)
				if item.uom != prev_item.uom:
					# mismatch in UOM
					errmsg("uom", item, prev_item)
