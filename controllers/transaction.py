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
import webnotes.model
from webnotes.utils import cint

from webnotes.model.controller import DocListController
class TransactionController(DocListController):
	def set_schedule_date(self, table_field=None):
		"""set schedule date in items as posting_date + lead_time_days"""
		prevdoc_fields = webnotes.model.get_prevdoc_fields(self.doctype)
		
		if not table_field:
			table_field = webnotes.form_dict.get("table_field")
		
		for d in self.doclist.get({"parenfield": table_field}):
			lead_time_days = webnotes.conn.sql("""select ifnull(lead_time_days, 0)
				from `tabItem` where name=%s and (ifnull(end_of_life, "")="" 
				or end_of_life="0000-00-00" or end_of_life > now())""", (d.item_code,))
			lead_time_days = lead_time_days and cint(lead_time_days[0][0]) or 0

			if lead_time_days:
				d.lead_time_date = add_days(self.doc.posting_date, lead_time_days)
				if not any([d.fields.get(f) for f in prevdoc_fields]):
					# i.e. if not mapped using doctype mapper
					d.schedule_date = add_days(self.doc.posting_date, lead_time_days)
		