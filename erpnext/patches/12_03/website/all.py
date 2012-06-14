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

import patches.12_03.website.login
import patches.12_03.website.feed
import patches.12_03.website.website
import patches.12_03.website.cleanups
import patches.12_03.website.domain_list
import patches.12_03.website.file_data_rename
import patches.12_03.website.analytics
import patches.12_03.website.allow_product_delete


def execute():
	patches.12_03.website.login.execute()
	patches.12_03.website.feed.execute()
	patches.12_03.website.website.execute()
	patches.12_03.website.cleanups.execute()
	patches.12_03.website.domain_list.execute()
	patches.12_03.website.file_data_rename.execute()
	patches.12_03.website.analytics.execute()
	patches.12_03.website.allow_product_delete.execute()
