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
from webnotes.model.controller import DocListController
from webnotes.model.rename_doc import rename_doc
import webnotes

class RenameToolController(DocListController):
	def rename(self):
		"""rename items from file"""
		renamed = []
		for d in self.get_csv_from_attachment():
			rename_doc(self.doc.rename_doctype, d[0], d[1])
			renamed.append(d)
		
		for r in renamed:
			webnotes.msgprint(d[0] + " renamed to " + d[1])
			
		self.doc.rename_doctype = None
		self.doc.save()
