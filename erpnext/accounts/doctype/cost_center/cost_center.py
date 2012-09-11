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
from webnotes.utils import cstr
from webnotes.utils.nestedset import NestedSetController

class CostCenterController(NestedSetController):
	def setup(self):
		self.nsm_parent_field = 'parent_cost_center'

	def autoname(self):
		abbr = self.session.db.get_value('Company', self.doc.company_name, 'abbr')
		self.doc.name = cstr(self.doc.cost_center_name) + ' - ' + abbr
		
	def validate(self):
		self.validate_mandatory()
		self.validate_duplicate_cost_center()
		self.validate_budget_against_group()
	
	def validate_mandatory(self):
		if not self.doc.group_or_ledger:
			self.session.msgprint(_("Please select Group or Ledger value"), 
				raise_exception=webnotes.MandatoryError)			
		if self.doc.cost_center_name != 'Root' and not self.doc.parent_cost_center:
			self.session.msgprint(_("Please enter parent cost center"), 
				raise_exception=webnotes.MandatoryError)
		if self.doc.cost_center_name =='Root' and self.doc.parent_cost_center:
			self.session.msgprint(_("Root cost center can not have a parent"), 
				raise_exception=webnotes.MandatoryError)
		
	def validate_duplicate_cost_center(self):
		"""Cost Center name must be unique"""		
		if (self.doc.__islocal or not self.doc.name) and self.session.db.exists("Cost Center", \
			{'cost_center_name': self.doc.cost_center_name, 'company_name': self.doc.company_name}):
			self.session.msgprint(_("Cost Center Name already exists, please rename"), 
				raise_exception=webnotes.NameError)
			
	def validate_budget_against_group(self):
		if self.doc.group_or_ledger=="Group" and self.doclist.get({"parentfield": "budget_details"}):
			self.session.msgprint(_("Budget cannot be set for Group Cost Centers"), 
				raise_exception=1)
		
	def convert_group_to_ledger(self):
		if self.session.db.exists('Cost Center', {'parent_cost_center': self.doc.name}):
			self.session.msgprint(_("""Cost Center: %s has existing child. You can not convert
				this cost center to ledger.	To proceed, move those children under
				another parent and try again""")
				% self.doc.name, raise_exception=webnotes.ValidationError)
		else:
			self.session.db.set(self.doc, 'group_or_ledger', 'Ledger')
			return 1
			
	def convert_ledger_to_group(self):
		if self.session.db.exists('GL Entry', {'cost_center': self.doc.name}):
			self.session.msgprint(_("Cost Center with existing transaction can not be converted to group."), 
				raise_exception=webnotes.ValidationError)
		else:
			self.session.db.set(self.doc, 'group_or_ledger', 'Group')
			return 1