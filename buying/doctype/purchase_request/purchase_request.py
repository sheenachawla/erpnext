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

from controllers.transaction import TransactionController

class DocType(TransactionController):
	def __init__(self, doc, doclist):
		self.doc, self.doclist = doc, doclist
		
	def validate(self):
		if self.doc.status == "Stopped":
			# stop purchase request
			# kba update_status
			pass
			
		elif self.doc.status == "Submitted":
			# resume purchase request
			# kba update_status
			pass
		
	def on_update(self):
		pass
		
	def on_submit(self):
		pass
		
	def on_cancel(self):
		pass
		
	def on_trash(self):
		pass
		
	
# =======
# 		# Validate qty against SO
# 		self.validate_qty_against_so()
# 
# 	
# 	def update_bin(self, is_submit, is_stopped):
# 		""" Update Quantity Requested for Purchase in Bin"""
# 		
# 		for d in getlist(self.doclist, 'indent_details'):
# 			if webnotes.conn.get_value("Item", d.item_code, "is_stock_item") == "Yes":
# 				if not d.warehouse:
# 					msgprint("Please Enter Warehouse for Item %s as it is stock item" 
# 						% cstr(d.item_code), raise_exception=1)
# 						
# 				qty =flt(d.qty)
# 				if is_stopped:
# 					qty = (d.qty > d.ordered_qty) and flt(flt(d.qty) - flt(d.ordered_qty)) or 0
# 				
# 				args = {
# 					"item_code": d.item_code,
# 					"indented_qty": (is_submit and 1 or -1) * flt(qty),
# 					"posting_date": self.doc.transaction_date
# 				}
# 				get_obj('Warehouse', d.warehouse).update_bin(args)		
# 		
# 	def on_submit(self):
# 		set(self.doc,'status','Submitted')
# 		self.update_bin(is_submit = 1, is_stopped = 0)
# 	
# 	def check_modified_date(self):
# 		mod_db = sql("select modified from `tabPurchase Request` where name = '%s'" % self.doc.name)
# 		date_diff = sql("select TIMEDIFF('%s', '%s')" % ( mod_db[0][0],cstr(self.doc.modified)))
# 		
# 		if date_diff and date_diff[0][0]:
# 			msgprint(cstr(self.doc.doctype) +" => "+ cstr(self.doc.name) +" has been modified. Please Refresh. ")
# 			raise Exception
# 
# 	def update_status(self, status):
# 		self.check_modified_date()
# 		# Step 1:=> Update Bin
# 		self.update_bin(is_submit = (status == 'Submitted') and 1 or 0, is_stopped = 1)
# 
# 		# Step 2:=> Set status 
# 		set(self.doc,'status',cstr(status))
# 		
# 		# Step 3:=> Acknowledge User
# 		msgprint(self.doc.doctype + ": " + self.doc.name + " has been %s." % ((status == 'Submitted') and 'Unstopped' or cstr(status)) )
#  
# 
# >>>>>>> master