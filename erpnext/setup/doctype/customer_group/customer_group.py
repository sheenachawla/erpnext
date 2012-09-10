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

from webnotes import msgprint
	

from webnotes.model.controller import DocListController
class CustomerGroupController(DocListController):
	def setup(self):
		self.nsm_parent_field = 'parent_customer_group';


	# update Node Set Model
	def update_nsm_model(self):
		import webnotes
		import webnotes.utils.nestedset
		webnotes.utils.nestedset.update_nsm(self)

	# ON UPDATE
	#--------------------------------------
	def on_update(self):
		# update nsm
		self.update_nsm_model()   


	def validate(self):
		if self.doc.customer_group_name and self.session.db.sql("""select name from `tabCustomer Group`
			where name = %s and docstatus = 2""", self.doc.customer_group_name):
			msgprint("""Another %s record is trashed. 
				To untrash please go to Setup & click on Trash."""%(self.doc.customer_group_name), raise_exception = 1)

	def on_trash(self):
		cust = self.session.db.sql("select name from `tabCustomer` where ifnull(customer_group, '') = %s", self.doc.name)
		cust = [d[0] for d in cust]
		
		if cust:
			msgprint("""Customer Group: %s can not be trashed/deleted because it is used in customer: %s. 
				To trash/delete this, remove/change customer group in customer master""" % (self.doc.name, cust or ''), raise_exception=1)

		if self.session.db.sql("select name from `tabCustomer Group` where parent_customer_group = %s and docstatus != 2", self.doc.name):
			msgprint("Child customer group exists for this customer group. You can not trash/cancel/delete this customer group.", raise_exception=1)

		# rebuild tree
		self.session.db.set(self.doc,'old_parent', '')
		self.update_nsm_model()
