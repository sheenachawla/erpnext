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
from webnotes.utils import cstr, date_diff, flt, getdate, now
from webnotes.model.doc import make_autoname
from webnotes.model.utils import getlist
from webnotes.model.controller import get_obj
from webnotes import msgprint

from controllers.selling_controller import SellingController

class DocType(SellingController):
	def setup(self):
		self.item_table_field = "sales_order_items"

	def validate(self):
		super(DocType, self).validate()
		self.validate_order_type()
		self.validate_po()
		self.doclist = sales_com_obj.make_packing_list(self,'sales_order_items')

		self.doc.status='Draft'
		if not self.doc.billing_status: self.doc.billing_status = 'Not Billed'
		if not self.doc.delivery_status: self.doc.delivery_status = 'Not Delivered'

	def pull_quotation_items(self):
		self.doclist = self.doc.clear_table(self.doclist, 'taxes_and_charges')
		self.doclist = self.doc.clear_table(self.doclist, 'sales_order_items')
		self.doclist = self.doc.clear_table(self.doclist, 'sales_team')
		
		if self.doc.quotation:
			mapper = webnotes.get_controller("DocType Mapper", "Quotation-Sales Order")

		import json
		from_to_list = [["Quotation", "Sales Order"], ["Quotation Item", "Sales Order Item"],
			["Sales Taxes and Charges", "Sales Taxes and Charges"], ["Sales Team", "Sales Team"]]
		
		mapper.dt_map("Quotation", "Sales Order", self.doc.quotation,
			self.doc, self.doclist, json.dumps(from_to_list))
			
# 	def get_contact_details(self):
# 		get_obj('Sales Common').get_contact_details(self,0)
# 
# 
# 	# Get Tax rate if account type is TAX
# 	# ------------------------------------
# 	def get_rate(self,arg):
# 		return get_obj('Sales Common').get_rate(arg)
# 

#check if maintenance schedule already generated
#============================================
	def check_maintenance_schedule(self):
		nm = webnotes.conn.sql("select t1.name from `tabMaintenance Schedule` t1, `tabMaintenance Schedule Item` t2 where t2.parent=t1.name and t2.prevdoc_docname=%s and t1.docstatus=1", self.doc.name)
		nm = nm and nm[0][0] or ''
		
		if not nm:
			return 'No'

	def check_maintenance_visit(self):
		nm = webnotes.conn.sql("""select t1.name from `tabMaintenance Visit` t1, 
			`tabMaintenance Visit Purpose` t2 where t2.parent=t1.name and t2.prevdoc_docname=%s 
			and t1.docstatus=1 and t1.completion_status='Fully Completed'""", self.doc.name)
		nm = nm and nm[0][0] or ''
		if not nm:
			return 'No'

	def validate_mandatory(self):
		super(DocType, self).validate_mandatory()
		if self.doc.delivery_date:
			if getdate(self.doc.posting_date) > getdate(self.doc.delivery_date):
				msgprint("Expected Delivery Date cannot be before Sales Order Date")
				raise Exception

	def validate_po(self):
		if self.doc.po_date and self.doc.delivery_date and getdate(self.doc.po_date) > getdate(self.doc.delivery_date):
			msgprint("Expected Delivery Date cannot be before Purchase Order Date")
			raise Exception	
		
		if self.doc.po_no and self.doc.customer:
			so = webnotes.conn.webnotes.conn.sql("select name from `tabSales Order` \
				where ifnull(po_no, '') = %s and name != %s and docstatus < 2\
				and customer = %s", (self.doc.po_no, self.doc.name, self.doc.customer))
			if so and so[0][0]:
				msgprint("""Another Sales Order (%s) exists against same PO No and Customer. 
					Please be sure, you are not making duplicate entry.""" % so[0][0])
	
	def validate_for_items(self):
		check_list,flag = [],0
		chk_dupl_itm = []
		# Sales Order Items Validations
		for d in getlist(self.doclist, 'sales_order_items'):
			if cstr(self.doc.quotation) == cstr(d.prevdoc_docname):
				flag = 1
			if d.prevdoc_docname:
				if self.doc.quotation_date and getdate(self.doc.quotation_date) > getdate(self.doc.posting_date):
					msgprint("Sales Order Date cannot be before Quotation Date")
					raise Exception
				# validates whether quotation no in doctype and in table is same
				if not cstr(d.prevdoc_docname) == cstr(self.doc.quotation):
					msgprint("Items in table does not belong to the Quotation No mentioned.")
					raise Exception

			# validates whether item is not entered twice
			e = [d.item_code, d.description, d.warehouse, d.prevdoc_docname or '']
			f = [d.item_code, d.description]

			#check item is stock item
			st_itm = webnotes.conn.sql("select is_stock_item from `tabItem` where name = '%s'"%d.item_code)

			if st_itm and st_itm[0][0] == 'Yes':
				if e in check_list:
					msgprint("Item %s has been entered twice." % d.item_code)
				else:
					check_list.append(e)
			elif st_itm and st_itm[0][0]== 'No':
				if f in chk_dupl_itm:
					msgprint("Item %s has been entered twice." % d.item_code)
				else:
					chk_dupl_itm.append(f)

			# used for production plan
			d.posting_date = self.doc.posting_date
			d.delivery_date = self.doc.delivery_date

			# gets total projected qty of item in warehouse selected (this case arises when warehouse is selected b4 item)
			tot_avail_qty = webnotes.conn.sql("select projected_qty from `tabBin` where item_code = '%s' and warehouse = '%s'" % (d.item_code,d.warehouse))
			d.projected_qty = tot_avail_qty and flt(tot_avail_qty[0][0]) or 0
		
		if flag == 0:
			msgprint("There are no items of the quotation selected.")
			raise Exception

	def validate_sales_mntc_quotation(self):
		for d in getlist(self.doclist, 'sales_order_items'):
			if d.prevdoc_docname:
				res = webnotes.conn.sql("select name from `tabQuotation` where name=%s and order_type = %s", (d.prevdoc_docname, self.doc.order_type))
				if not res:
					msgprint("""Order Type (%s) should be same in Quotation: %s \
						and current Sales Order""" % (self.doc.order_type, d.prevdoc_docname))

	def validate_order_type(self):
		if self.doc.order_type == 'Sales' and not self.doc.delivery_date:
			msgprint("Please enter 'Expected Delivery Date'")
			raise Exception
		
		self.validate_sales_mntc_quotation()

	def validate_proj_cust(self):
		if self.doc.project_name and self.doc.customer_name:
			res = webnotes.conn.sql("select name from `tabProject` where name = '%s' and (customer = '%s' or ifnull(customer,'')='')"%(self.doc.project_name, self.doc.customer))
			if not res:
				msgprint("Customer - %s does not belong to project - %s. \n\nIf you want to use project for multiple customers then please make customer details blank in project - %s."%(self.doc.customer,self.doc.project_name,self.doc.project_name))
				raise Exception
			 

	# Validate
	# ---------

		
	def check_prev_docstatus(self):
		for d in getlist(self.doclist, 'sales_order_items'):
			cancel_quo = webnotes.conn.sql("select name from `tabQuotation` where docstatus = 2 and name = '%s'" % d.prevdoc_docname)
			if cancel_quo:
				msgprint("Quotation :" + cstr(cancel_quo[0][0]) + " is already cancelled !")
				raise Exception , "Validation Error. "
	
	def update_enquiry_status(self, prevdoc, flag):
		enq = webnotes.conn.sql("select t2.prevdoc_docname from `tabQuotation` t1, `tabQuotation Item` t2 where t2.parent = t1.name and t1.name=%s", prevdoc)
		if enq:
			webnotes.conn.sql("update `tabOpportunity` set status = %s where name=%s",(flag,enq[0][0]))


	def update_prevdoc_status(self, flag):
		for d in getlist(self.doclist, 'sales_order_items'):
			if d.prevdoc_docname:
				if flag=='submit':
					webnotes.conn.sql("update `tabQuotation` set status = 'Order Confirmed' where name=%s",d.prevdoc_docname)
					
					self.update_enquiry_status(d.prevdoc_docname, 'Order Confirmed')
				elif flag == 'cancel':
					chk = webnotes.conn.sql("select t1.name from `tabSales Order` t1, `tabSales Order Item` t2 where t2.parent = t1.name and t2.prevdoc_docname=%s and t1.name!=%s and t1.docstatus=1", (d.prevdoc_docname,self.doc.name))
					if not chk:
						webnotes.conn.sql("update `tabQuotation` set status = 'Submitted' where name=%s",d.prevdoc_docname)
						
						#update enquiry
						self.update_enquiry_status(d.prevdoc_docname, 'Quotation Sent')
	
	def on_submit(self):
		self.check_prev_docstatus()		
		self.update_stock_ledger(update_stock = 1)
		# update customer's last sales order no.
		update_customer = webnotes.conn.sql("update `tabCustomer` set last_sales_order = '%s', modified = '%s' where name = '%s'" %(self.doc.name, self.doc.modified, self.doc.customer))
		get_obj('Sales Common').check_credit(self,self.doc.grand_total)
		
		# Check for Approving Authority
		get_obj('Authorization Control').validate_approving_authority(self.doc.doctype, self.doc.grand_total, self)
		
		self.update_prevdoc_status('submit')
		webnotes.conn.set(self.doc, 'status', 'Submitted')
	
	def on_cancel(self):
		# Cannot cancel stopped SO
		if self.doc.status == 'Stopped':
			msgprint("Sales Order : '%s' cannot be cancelled as it is Stopped. Unstop it for any further transactions" %(self.doc.name))
			raise Exception
		self.check_nextdoc_docstatus()
		self.update_stock_ledger(update_stock = -1)
		self.update_prevdoc_status('cancel')
		webnotes.conn.set(self.doc, 'status', 'Cancelled')
		
	def check_nextdoc_docstatus(self):
		# Checks Delivery Note
		submit_dn = webnotes.conn.sql("select t1.name from `tabDelivery Note` t1,`tabDelivery Note Item` t2 where t1.name = t2.parent and t2.prevdoc_docname = '%s' and t1.docstatus = 1" % (self.doc.name))
		if submit_dn:
			msgprint("Delivery Note : " + cstr(submit_dn[0][0]) + " has been submitted against " + cstr(self.doc.doctype) + ". Please cancel Delivery Note : " + cstr(submit_dn[0][0]) + " first and then cancel "+ cstr(self.doc.doctype), raise_exception = 1)
		# Checks Sales Invoice
		submit_rv = webnotes.conn.sql("select t1.name from `tabSales Invoice` t1,`tabSales Invoice Item` t2 where t1.name = t2.parent and t2.sales_order = '%s' and t1.docstatus = 1" % (self.doc.name))
		if submit_rv:
			msgprint("Sales Invoice : " + cstr(submit_rv[0][0]) + " has already been submitted against " +cstr(self.doc.doctype)+ ". Please cancel Sales Invoice : "+ cstr(submit_rv[0][0]) + " first and then cancel "+ cstr(self.doc.doctype), raise_exception = 1)
		#check maintenance schedule
		submit_ms = webnotes.conn.sql("select t1.name from `tabMaintenance Schedule` t1, `tabMaintenance Schedule Item` t2 where t2.parent=t1.name and t2.prevdoc_docname = %s and t1.docstatus = 1",self.doc.name)
		if submit_ms:
			msgprint("Maintenance Schedule : " + cstr(submit_ms[0][0]) + " has already been submitted against " +cstr(self.doc.doctype)+ ". Please cancel Maintenance Schedule : "+ cstr(submit_ms[0][0]) + " first and then cancel "+ cstr(self.doc.doctype), raise_exception = 1)
		submit_mv = webnotes.conn.sql("select t1.name from `tabMaintenance Visit` t1, `tabMaintenance Visit Purpose` t2 where t2.parent=t1.name and t2.prevdoc_docname = %s and t1.docstatus = 1",self.doc.name)
		if submit_mv:
			msgprint("Maintenance Visit : " + cstr(submit_mv[0][0]) + " has already been submitted against " +cstr(self.doc.doctype)+ ". Please cancel Maintenance Visit : " + cstr(submit_mv[0][0]) + " first and then cancel "+ cstr(self.doc.doctype), raise_exception = 1)


	def check_modified_date(self):
		mod_db = webnotes.conn.sql("select modified from `tabSales Order` where name = '%s'" % self.doc.name)
		date_diff = webnotes.conn.sql("select TIMEDIFF('%s', '%s')" % ( mod_db[0][0],cstr(self.doc.modified)))
		if date_diff and date_diff[0][0]:
			msgprint("%s: %s has been modified after you have opened. Please Refresh"
				% (self.doc.doctype, self.doc.name), raise_exception=1)

	def stop_sales_order(self):
		self.check_modified_date()
		self.update_stock_ledger(update_stock = -1,clear = 1)
		webnotes.conn.set(self.doc, 'status', 'Stopped')
		msgprint("""%s: %s has been Stopped. To make transactions against this Sales Order 
			you need to Unstop it.""" % (self.doc.doctype, self.doc.name))

	def unstop_sales_order(self):
		self.check_modified_date()
		self.update_stock_ledger(update_stock = 1,clear = 1)
		webnotes.conn.set(self.doc, 'status', 'Submitted')
		msgprint("%s: %s has been Unstopped" % (self.doc.doctype, self.doc.name))

	def update_stock_ledger(self, update_stock, clear = 0):
		for d in self.get_item_list(clear):
			if webnotes.conn.get_value("Item", d['item_code'], "is_stock_item") == "Yes":
				if not d['warehouse']:
					msgprint("""Please enter Reserved Warehouse for item %s 
						as it is stock ite""" % d['item_code'], raise_exception=1)
						
				args = {
					"item_code": d['item_code'],
					"reserved_qty": flt(update_stock) * flt(d['qty']),
					"posting_date": self.doc.transaction_date,
					"voucher_type": self.doc.doctype,
					"voucher_no": self.doc.name,
					"is_amended": self.doc.amended_from and 'Yes' or 'No'
				}
				get_obj('Warehouse', d['warehouse']).update_bin(args)
				
				
	def get_item_list(self, clear):
		return get_obj('Sales Common').get_item_list( self, clear)

	def on_update(self):
		pass
