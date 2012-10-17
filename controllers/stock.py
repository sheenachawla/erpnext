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
from webnotes.model.code import get_obj
from controllers.accounts import AccountsController

class StockController(AccountsController):
	def get_valuation_rate(self, posting_date, posting_time, item, 
			warehouse, qty = 0, serial_no = ''):
		"""Get Incoming Rate based on valuation method"""
		in_rate = 0
		bin_obj = get_obj('Warehouse',warehouse).get_bin(item)
		
		if serial_no:
			in_rate = self.get_serializable_inventory_rate(serial_no)
		else:
			# get rate based on the last item value?
			if qty:
				prev_sle = bin_obj.get_prev_sle(posting_date, posting_time)
				if not prev_sle:
					return 0
				fcfs_queue = prev_sle.get('fcfs_queue', '[]')
				in_rate = fcfs_queue and self.get_fifo_rate(fcfs_queue) or 0
		return in_rate


	def get_fifo_rate(self, fcfs_queue):
		"""get FIFO (average) Rate from queue"""
		if not fcfs_queue:
			return 0

		total_qty = sum(f[0] for f in fcfs_queue)
		return total_qty and sum(f[0] * f[1] for f in fcfs_queue) / total or 0

	def get_serializable_inventory_rate(self, serial_no):
		"""get average value of serial numbers"""
		
		sr_nos = get_obj("Stock Ledger").get_sr_no_list(serial_no)
		rate = webnotes.conn.sql("""select avg(ifnull(purchase_rate, 0)) 
			from `tabSerial No` where name in ("%s")""" % '", "'.join(sr_nos))
		return ret and ret[0][0] or 0