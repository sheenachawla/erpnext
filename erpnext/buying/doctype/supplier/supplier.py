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

from webnotes.utils import cstr, get_defaults

from webnotes.model.doc import make_autoname
from webnotes.model.code import get_obj
from webnotes import msgprint
from controllers.party import PartyController

class SupplierController(PartyController):
	def autoname(self):
		self.create_name('supp_master_name', 'Supplier Name', 'Customer')
		
	def validate(self):
		self.validate_series('supp_master_name')
		
	def on_update(self):
		self.create_supplier_ledger()
		self.update_credit_days_limit()
		
	def create_supplier_ledger(self):
		self.create_account({
			'parent_account': self.get_parent_account(),
			'supplier': self.doc.name
		})

	def get_parent_account(self):
		"""
		Returns parent account that is account for supplier type
		If not exists, create it
		"""
		if not self.doc.supplier_type:
			msgprint("Supplier Type is mandatory", raise_exception=MandatoryError)

		supp_type_acc = webnotes.conn.get_value('Account', {'account_name': self.doc.supplier_type, \
			'company': self.doc.company, 'debit_or_credit': 'Credit', 'is_pl_account': 'No'})

		# if group not created for supplier_type, create it
		if not supp_type_acc:
			supp_type_acc = self.create_account({
				'account_name': self.doc.supplier_type,
				'parent_account': self.get_party_group('payables_group'),
				'group_or_ledger': 'Group'
			})
		return supp_type_acc