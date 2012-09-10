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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.	If not, see <http://www.gnu.org/licenses/>.

import webnotes

from webnotes.utils import flt

from webnotes.utils.nestedset import NestedSetController
	
class TerritoryController(NestedSetController):
	def setup(self):
		self.nsm_parent_field = 'parent_territory'

	def validate(self):
		for d in self.doclist.get({"parentfield": "target_details"}):
			if not flt(d.target_qty) and not flt(d.target_amount):
				msgprint("Either target qty or target amount is mandatory.", raise_exception=1)