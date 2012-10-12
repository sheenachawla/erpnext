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

# Please edit this list and import only required elements
from __future__ import unicode_literals
import webnotes

from webnotes.utils import add_days, add_months, add_years, cint, cstr, date_diff, default_fields, flt, fmt_money, formatdate, getTraceback, get_defaults, get_first_day, get_last_day, getdate, has_common, month_name, now, nowdate, replace_newlines, sendmail, set_default, str_esc_quote, user_format, validate_email_add
from webnotes.model import db_exists
from webnotes.model.doc import Document, addchild, getchildren, make_autoname
from webnotes.model.utils import getlist
from webnotes.model.code import get_obj, get_server_obj, run_server_obj, updatedb, check_syntax
from webnotes import session, form, msgprint, errprint

set = webnotes.conn.set
sql = webnotes.conn.sql
get_value = webnotes.conn.get_value
in_transaction = webnotes.conn.in_transaction
convert_to_lists = webnotes.conn.convert_to_lists
	
# -----------------------------------------------------------------------------------------

from utilities.transaction_base import TransactionBase

class DocType(TransactionBase):
	def __init__(self, doc, doclist=[]):
		self.doc = doc
		self.doclist = doclist
		self.defaults = get_defaults()
		self.tname = 'Purchase Order Item'
		self.fname = 'po_details'

	# Autoname
	# ---------
	def autoname(self):
		self.doc.name = make_autoname(self.doc.naming_series+'.#####')

	def get_default_schedule_date(self):
		get_obj(dt = 'Purchase Common').get_default_schedule_date(self)
		
	def validate_fiscal_year(self):
		get_obj(dt = 'Purchase Common').validate_fiscal_year(self.doc.fiscal_year,self.doc.transaction_date,'PO Date')


	# Get Item Details
	def get_item_details(self, arg =''):
		import json
		if arg:
			return get_obj(dt='Purchase Common').get_item_details(self,arg)
		else:
			obj = get_obj('Purchase Common')
			for doc in self.doclist:
				if doc.fields.get('item_code'):
					temp = {
						'item_code': doc.fields.get('item_code'),
						'warehouse': doc.fields.get('warehouse')
					}
					ret = obj.get_item_details(self, json.dumps(temp))
					for r in ret:
						if not doc.fields.get(r):
							doc.fields[r] = ret[r]



	# Get UOM Details
	def get_uom_details(self, arg = ''):
		return get_obj('Purchase Common').get_uom_details(arg)

	# get available qty at warehouse
	def get_bin_details(self, arg = ''):
		return get_obj(dt='Purchase Common').get_bin_details(arg)

	# Pull Purchase Request
	def get_indent_details(self):
		if self.doc.indent_no:
			get_obj('DocType Mapper','Purchase Request-Purchase Order').dt_map('Purchase Request','Purchase Order',self.doc.indent_no, self.doc, self.doclist, "[['Purchase Request','Purchase Order'],['Purchase Request Item', 'Purchase Order Item']]")
			pcomm = get_obj('Purchase Common')
			for d in getlist(self.doclist, 'po_details'):
				if d.item_code and not d.purchase_rate:
					last_purchase_details, last_purchase_date = pcomm.get_last_purchase_details(d.item_code, self.doc.name)
					if last_purchase_details:
						conversion_factor = d.conversion_factor or 1.0
						conversion_rate = self.doc.fields.get('conversion_rate') or 1.0
						d.purchase_ref_rate = last_purchase_details['purchase_ref_rate'] * conversion_factor
						d.discount_rate = last_purchase_details['discount_rate']
						d.purchase_rate = last_purchase_details['purchase_rate'] * conversion_factor
						d.import_ref_rate = d.purchase_ref_rate / conversion_rate
						d.import_rate = d.purchase_rate / conversion_rate						
					else:
						d.purchase_ref_rate = d.discount_rate = d.purchase_rate = d.import_ref_rate = d.import_rate = 0.0
						
	def get_supplier_quotation_items(self):
		if self.doc.supplier_quotation:
			get_obj("DocType Mapper", "Supplier Quotation-Purchase Order").dt_map("Supplier Quotation",
				"Purchase Order", self.doc.supplier_quotation, self.doc, self.doclist,
				"""[['Supplier Quotation', 'Purchase Order'],
				['Supplier Quotation Item', 'Purchase Order Item'],
				['Purchase Taxes and Charges', 'Purchase Taxes and Charges']]""")
			self.get_default_schedule_date()
			for d in getlist(self.doclist, 'po_details'):
				if d.prevdoc_detail_docname and not d.schedule_date:
					d.schedule_date = webnotes.conn.get_value("Purchase Request Item",
							d.prevdoc_detail_docname, "schedule_date")
	
	def get_tc_details(self):
		"""get terms & conditions"""
		return get_obj('Purchase Common').get_tc_details(self)

	def get_last_purchase_rate(self):
		get_obj('Purchase Common').get_last_purchase_rate(self)
		
	def validate_doc(self,pc_obj):
		# Validate values with reference document
		pc_obj.validate_reference_value(obj = self)

	# Check for Stopped status 
	def check_for_stopped_status(self, pc_obj):
		check_list =[]
		for d in getlist(self.doclist, 'po_details'):
			if d.fields.has_key('prevdoc_docname') and d.prevdoc_docname and d.prevdoc_docname not in check_list:
				check_list.append(d.prevdoc_docname)
				pc_obj.check_for_stopped_status( d.prevdoc_doctype, d.prevdoc_docname)

		
	# Validate
	def validate(self):
		self.validate_fiscal_year()
		# Step 1:=> set status as "Draft"
		set(self.doc, 'status', 'Draft')
		
		# Step 2:=> get Purchase Common Obj
		pc_obj = get_obj(dt='Purchase Common')
		
		# Step 3:=> validate mandatory
		pc_obj.validate_mandatory(self)

		# Step 4:=> validate for items
		pc_obj.validate_for_items(self)

		# Step 5:=> validate conversion rate
		pc_obj.validate_conversion_rate(self)
		
		# Get po date
		pc_obj.get_prevdoc_date(self)
		
		# validate_doc
		self.validate_doc(pc_obj)
		
		# Check for stopped status
		self.check_for_stopped_status(pc_obj)
		
			
		 # get total in words
		dcc = TransactionBase().get_company_currency(self.doc.company)
		self.doc.in_words = pc_obj.get_total_in_words(dcc, self.doc.grand_total)
		self.doc.in_words_import = pc_obj.get_total_in_words(self.doc.currency, self.doc.grand_total_import)
	
	# update bin
	# ----------
	def update_bin(self, is_submit, is_stopped = 0):
		pc_obj = get_obj('Purchase Common')
		for d in getlist(self.doclist, 'po_details'):
			#1. Check if is_stock_item == 'Yes'
			if sql("select is_stock_item from tabItem where name=%s", d.item_code)[0][0]=='Yes':
				
				ind_qty, po_qty = 0, flt(d.qty) * flt(d.conversion_factor)
				if is_stopped:
					po_qty = flt(d.qty) > flt(d.received_qty) and flt( flt(flt(d.qty) - flt(d.received_qty)) * flt(d.conversion_factor))or 0 
				
				# No updates in Purchase Request on Stop / Unstop
				if cstr(d.prevdoc_doctype) == 'Purchase Request' and not is_stopped:
					# get qty and pending_qty of prevdoc 
					curr_ref_qty = pc_obj.get_qty( d.doctype, 'prevdoc_detail_docname', d.prevdoc_detail_docname, 'Purchase Request Item', 'Purchase Request - Purchase Order', self.doc.name)
					max_qty, qty, curr_qty = flt(curr_ref_qty.split('~~~')[1]), flt(curr_ref_qty.split('~~~')[0]), 0
					
					if flt(qty) + flt(po_qty) > flt(max_qty):
						curr_qty = flt(max_qty) - flt(qty)
						# special case as there is no restriction for Purchase Request - Purchase Order 
						curr_qty = (curr_qty > 0) and curr_qty or 0
					else:
						curr_qty = flt(po_qty)
					
					ind_qty = -flt(curr_qty)

				#==> Update Bin's Purchase Request Qty by +- ind_qty and Ordered Qty by +- qty
				get_obj('Warehouse', d.warehouse).update_bin(0, 0, (is_submit and 1 or -1) * flt(po_qty), (is_submit and 1 or -1) * flt(ind_qty), 0, d.item_code, self.doc.transaction_date)

	def check_modified_date(self):
		mod_db = sql("select modified from `tabPurchase Order` where name = '%s'" % self.doc.name)
		date_diff = sql("select TIMEDIFF('%s', '%s')" % ( mod_db[0][0],cstr(self.doc.modified)))
		
		if date_diff and date_diff[0][0]:
			msgprint(cstr(self.doc.doctype) +" => "+ cstr(self.doc.name) +" has been modified. Please Refresh. ")
			raise Exception

	# On Close
	#-------------------------------------------------------------------------------------------------
	def update_status(self, status):
		self.check_modified_date()
		# step 1:=> Set Status
		set(self.doc,'status',cstr(status))

		# step 2:=> Update Bin
		self.update_bin(is_submit = (status == 'Submitted') and 1 or 0, is_stopped = 1)

		# step 3:=> Acknowledge user
		msgprint(self.doc.doctype + ": " + self.doc.name + " has been %s." % ((status == 'Submitted') and 'Unstopped' or cstr(status)))


	# On Submit
	def on_submit(self):
		pc_obj = get_obj(dt ='Purchase Common')
		
		# Step 1 :=> Update Previous Doc i.e. update pending_qty and Status accordingly
		pc_obj.update_prevdoc_detail(self, is_submit = 1)

		# Step 2 :=> Update Bin 
		self.update_bin(is_submit = 1, is_stopped = 0)
		
		# Step 3 :=> Check For Approval Authority
		get_obj('Authorization Control').validate_approving_authority(self.doc.doctype, self.doc.company, self.doc.grand_total)
		
		# Step 4 :=> Update Current PO No. in Supplier as last_purchase_order.
		update_supplier = webnotes.conn.set_value("Supplier", self.doc.supplier,
			"last_purchase_order", self.doc.name)

		# Step 5 :=> Update last purchase rate
		pc_obj.update_last_purchase_rate(self, is_submit = 1)

		# Step 6 :=> Set Status
		set(self.doc,'status','Submitted')
	 
	# On Cancel
	# -------------------------------------------------------------------------------------------------------
	def on_cancel(self):
		pc_obj = get_obj(dt = 'Purchase Common')
		
		# 1.Check if PO status is stopped
		pc_obj.check_for_stopped_status(cstr(self.doc.doctype), cstr(self.doc.name))
		
		self.check_for_stopped_status(pc_obj)
		
		# 2.Check if Purchase Receipt has been submitted against current Purchase Order
		pc_obj.check_docstatus(check = 'Next', doctype = 'Purchase Receipt', docname = self.doc.name, detail_doctype = 'Purchase Receipt Item')

		# 3.Check if Purchase Invoice has been submitted against current Purchase Order
		#pc_obj.check_docstatus(check = 'Next', doctype = 'Purchase Invoice', docname = self.doc.name, detail_doctype = 'Purchase Invoice Item')
		
		submitted = sql("select t1.name from `tabPurchase Invoice` t1,`tabPurchase Invoice Item` t2 where t1.name = t2.parent and t2.purchase_order = '%s' and t1.docstatus = 1" % self.doc.name)
		if submitted:
			msgprint("Purchase Invoice : " + cstr(submitted[0][0]) + " has already been submitted !")
			raise Exception

		# 4.Set Status as Cancelled
		set(self.doc,'status','Cancelled')

		# 5.Update Purchase Requests Pending Qty and accordingly it's Status 
		pc_obj.update_prevdoc_detail(self,is_submit = 0)
		
		# 6.Update Bin	
		self.update_bin( is_submit = 0, is_stopped = 0)
		
		# Step 7 :=> Update last purchase rate 
		pc_obj.update_last_purchase_rate(self, is_submit = 0)


	def on_update(self):
		get_obj("Purchase Common").update_subcontracting_raw_materials(self)		

	def get_rate(self,arg):
		return get_obj('Purchase Common').get_rate(arg,self)	
	
	def load_default_taxes(self):
		self.doclist = get_obj('Purchase Common').load_default_taxes(self)

	def get_purchase_tax_details(self):
		self.doclist = get_obj('Purchase Common').get_purchase_tax_details(self)
