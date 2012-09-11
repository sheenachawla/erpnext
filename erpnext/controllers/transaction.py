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
from webnotes.model import get_controller
from webnotes.model.controller import DocListController

class TrasactionController(DocListController):
	def validate_items_life(self):
		for child in self.doclist.get({"parentfield": self.item_table_fieldname}):
			get_controller("Item", child.item_code).check_end_of_life()
	
	# def validate_previous_doclist(self, fieldname, item_fieldname):
	# 	"""Validates current item row against previous item row"""
	# 	doctypelist = webnotes.model.get_doctype(self.doc.doctype)
	# 	prev_doctype = doctypelist.get_field(fieldname,
	# 	 	parentfield=self.item_table_fieldname).options
	# 
	# 	def errmsg(errfield, item, prev_item):
	# 		label = doctypelist.get_label(errfield, parent=item.doctype)
	# 		webnotes.msgprint("""%s of row # %d in the %s table
	# 			cannot be different from the one in row # %d in the %s table 
	# 			of %s: "%s" """ % (label, item.idx, item.doctype, prev_item.idx, 
	# 			prev_item.doctype, prev_doctype, item.get(fieldname)),
	# 			raise_exception=True)
	# 
	# 	prev_doclist_cache = {}
	# 	for item in self.doclist.get({"parentfield": self.item_table_fieldname}):
	# 		if item.get(fieldname):
	# 			prev_item = prev_doclist_cache.setdefault(item.get(fieldname),
	# 				webnotes.model.get(prev_doctype, name)).getone({
	# 					"name": item.get(item_fieldname)})
	# 			
	# 			if item.item_code != prev_item.item_code:
	# 				# mismatch in item code
	# 				errmsg("item_code", item, prev_item)
	# 			if item.warehouse != prev_item.warehouse:
	# 				# mismatch in warehouse
	# 				errmsg("warehouse", item, prev_item)
	# 			if item.uom != prev_item.uom:
	# 				# mismatch in UOM
	# 				errmsg("uom", item, prev_item)
