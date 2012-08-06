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

from website.web_page import PageController

class ItemController(PageController):
	def on_rename(self,newdn,olddn):
		webnotes.conn.sql("update tabItem set item_code = %s where name = %s", (newdn, olddn))

	def get_tax_rate(self, tax_type):
		from webnotes.utils import flt
		return { "tax_rate": flt(webnotes.conn.get_value("Account", tax_type, "tax_rate")) }

	def check_if_sle_exists(self):
		"""returns 'exists' or 'not exists'"""
		sle = webnotes.conn.get_value("Stock Ledger Entry",
			{"item_code": self.doc.name, "is_cancelled['No']": "No"}, "name")

		return sle and 'exists' or 'not exists'
