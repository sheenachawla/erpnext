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
from webnotes.utils import cint, flt
from webnotes.model.code import get_obj
sql = webnotes.conn.sql

class DocType:
	def __init__(self, doc, doclist):
		self.doc = doc
		self.doclist = doclist

	def calculate_cost(self, bom_no):
		main_bom_list = get_obj('Production Control').traverse_bom_tree( bom_no = bom_no, qty = 1, calculate_cost = 1)
		main_bom_list.reverse()
		for bom in main_bom_list:
			bom_obj = get_obj('BOM', bom, with_children = 1)
			bom_obj.calculate_cost()
		return 'calculated'