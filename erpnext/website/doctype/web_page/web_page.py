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
import website.utils
from website.web_page import PageController

class DocType(PageController):
	def autoname(self):
		"""name from title"""
		self.doc.name = website.utils.page_name(self.doc.title)

	def on_update(self):
		super(DocType, self).on_update()
		self.if_home_clear_cache()

	def if_home_clear(self):
		"""if home page, clear cache"""
		if self.session.bootinfo.home_page == self.doc.name:
			from webnotes.session_cache import delete_page_cache
			delete_page_cache(self.doc.name)
			delete_page_cache('index')
			
	def prepare_template_args(self):
		self.markdown_to_html(['head_section','main_section', 'side_section'])