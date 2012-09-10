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

"""
TO_DO:

* get actual qty on posting date for referrence
* amendment date if amended from
* get_item_details
* validate_approving_authority
* validate with predoc_details that item not changed after fetching
* check prevdoc is submitted and not stopped

"""

import webnotes
import webnotes.model
from webnotes.utils import cstr, flt, getdate
from webnotes import msgprint
from webnotes.model import get_controller
from controllers.stock import StockController

class DeliveryNoteController(StockController):
	def setup(self):
		self.item_table_fieldname = 'delivery_note_items'

	def validate(self):
		super(SalesOrderController, self).validate()
		self.so_required()
		if self.doc.docstatus == 1:
			self.check_credit_limit()
			
	def so_required(self):
		"""check in manage account if sales order required or not"""
		if webnotes.conn.get_value('Global Defaults', None, 'so_required') == 'Yes':
			 for d in getlist(self.doclist,'delivery_note_details'):
				 if not d.prevdoc_docname:
					 msgprint("Sales Order required against item %s" % 
						d.item_code, raise_exception=webnotes.ValidationError)
						
	def check_credit_limit(self):
		"""check credit limit for items which are not fetched from sales order"""
		amount = sum([d.amount for d in self.doclist.get({\
			'parentfield': 'delivery_note_items'}) if not d.sales_order])
		if amount > 0:
			total = (amount/self.doc.net_total)*self.doc.grand_total
			get_controller('Party',self.doc.party).check_credit_limit(self.doc.company, total)
			
	def on_submit(self):
		sl_obj = get_controller("Stock Ledger", None)
		sl_obj.validate_serial_no(self, 'delivery_note_details')
		sl_obj.validate_serial_no_warehouse(self, 'delivery_note_details')
		sl_obj.update_serial_record(self, 'delivery_note_details', is_submit = 1, is_incoming = 0)		
		self.update_stock_ledger(update_stock = 1)

	def on_cancel(self):
		sales_com_obj = get_controller(dt = 'Sales Common')
		sales_com_obj.check_stop_sales_order(self)
		
		sl = get_controller('Stock Ledger', None)		
		sl.update_serial_record(self, 'delivery_note_details', is_submit = 0, is_incoming = 0)
		sl.update_serial_record(self, 'packing_details', is_submit = 0, is_incoming = 0)

		self.update_stock_ledger(update_stock = -1)
		self.cancel_packing_slips()

	def cancel_packing_slips(self):
		"""
			Cancel submitted packing slips related to this delivery note
		"""
		res = webnotes.conn.sql("""\
			SELECT name, count(*) FROM `tabPacking Slip`
			WHERE delivery_note = %s AND docstatus = 1
			""", self.doc.name)

		if res and res[0][1]>0:
			for r in res:
				webnotes.model.get_controller("Packing Slip", r[0]).cancel()
			webnotes.msgprint("%s Packing Slip(s) Cancelled" % res[0][1])


	def update_stock_ledger(self, update_stock, is_stopped = 0):
		self.values = []
		for d in self.get_item_list(is_stopped):
			stock_item = webnotes.conn.sql("SELECT is_stock_item, is_sample_item FROM tabItem where name = '%s'"%(d['item_code']), as_dict = 1) # stock ledger will be updated only if it is a stock item
			if stock_item[0]['is_stock_item'] == "Yes":
				if not d['warehouse']:
					msgprint("Message: Please enter Warehouse for item %s as it is stock item."% d['item_code'])
					raise Exception
				if d['reserved_qty'] < 0 :
					# Reduce reserved qty from reserved warehouse mentioned in so
					bin = get_controller('Warehouse', d['reserved_warehouse']).update_bin(0, flt(update_stock) * flt(d['reserved_qty']), \
						0, 0, 0, d['item_code'], self.doc.transaction_date,doc_type=self.doc.doctype, \
						doc_name=self.doc.name, is_amended = (self.doc.amended_from and 'Yes' or 'No'))
						
				# Reduce actual qty from warehouse
				self.make_sl_entry(d, d['warehouse'], - flt(d['qty']) , 0, update_stock)
		get_controller('Stock Ledger', 'Stock Ledger').update_stock(self.values)


	def get_item_list(self, is_stopped):
	 return get_controller('Sales Common').get_item_list(self, is_stopped)


	def make_sl_entry(self, d, wh, qty, in_value, update_stock):
		self.values.append({
			'item_code'					: d['item_code'],
			'warehouse'					: wh,
			'transaction_date'			: getdate(self.doc.modified).strftime('%Y-%m-%d'),
			'posting_date'				: self.doc.posting_date,
			'posting_time'				: self.doc.posting_time,
			'voucher_type'				: 'Delivery Note',
			'voucher_no'				: self.doc.name,
			'voucher_detail_no'	 		: d['name'],
			'actual_qty'				: qty,
			'stock_uom'					: d['uom'],
			'incoming_rate'			 	: in_value,
			'company'					: self.doc.company,
			'fiscal_year'				: self.doc.fiscal_year,
			'is_cancelled'				: (update_stock==1) and 'No' or 'Yes',
			'batch_no'					: d['batch_no'],
			'serial_no'					: d['serial_no']
		})




	def on_update(self):
		sl = get_controller('Stock Ledger')
		sl.scrub_serial_nos(self)