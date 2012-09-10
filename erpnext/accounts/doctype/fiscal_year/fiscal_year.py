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
from webnotes.utils import cstr, add_days
from webnotes import msgprint
from webnotes.model.controller import DocListController

class FiscalYearController(DocListController):
	def validate(self):
		if webnotes.conn.sql("select name from `tabFiscal Year` where year_start_date < %s"\
			, self.doc.year_start_date) and not self.doc.past_year:
			msgprint("Please enter Past Year", raise_exception=webnotes.MandatoryError)

	def validate_date_within_year(self, dt, dt_label):
		yed=add_days(cstr(self.doc.year_start_date),365)
		if cstr(dt) < cstr(self.doc.year_start_date) or cstr(dt) > cstr(yed):
			msgprint("%s not within the fiscal year"%(field_label), raise_exception=webnotes.ValidationError)
