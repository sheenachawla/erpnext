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

# Material  Receipt
from __future__ import unicode_literals
mr = [
	{'doctype': 'Stock Entry', 'posting_date': '2012-09-01', 'transfer_date': '2012-09-01', 'posting_time': '12:00', 'company': 'Test Company', 'fiscal_year' : '2012-2013', 'purpose': 'Material Receipt', 'name': 'MR001'},
	{'doctype': 'Stock Entry Detail', 'parenttype': 'Stock Entry', 'parentfield' : 'mtn_details', 'parent' : 'MR001', 'name': 'SED001', 'item_code' : 'test_item', 't_warehouse' : 'test_wh1', 'qty' : 10, 'transfer_qty' : 10, 'incoming_rate': 100, 'stock_uom': 'Nos', 'conversion_factor': 1}
]

mr1 = [
	{'doctype': 'Stock Entry', 'posting_date': '2012-09-01', 'transfer_date': '2012-09-01', 'posting_time': '12:00', 'company': 'Test Company', 'fiscal_year' : '2012-2013', 'purpose': 'Material Receipt', 'name': 'MR002'}, 
	{'doctype': 'Stock Entry Detail', 'parenttype': 'Stock Entry', 'parentfield' : 'mtn_details', 'parent' : 'MR002', 'name': 'SED002', 'item_code' : 'test_item', 't_warehouse' : 'test_wh1', 'qty' : 5, 'transfer_qty' : 5, 'incoming_rate': 400, 'stock_uom': 'Nos', 'conversion_factor': 1}
]


# Material Transfer
mtn = [
	{'doctype': 'Stock Entry', 'posting_date': '2012-09-01', 'transfer_date': '2012-09-01', 'posting_time': '12:00', 'company': 'Test Company', 'fiscal_year' : '2012-2013', 'purpose': 'Material Transfer', 'name': 'MTN001'},
	{'doctype': 'Stock Entry Detail', 'parenttype': 'Stock Entry', 'parentfield' : 'mtn_details', 'parent' : 'MTN001', 'name': 'SED003', 'item_code' : 'test_item', 's_warehouse' : 'test_wh1', 't_warehouse' : 'test_wh2', 'qty' : 5, 'transfer_qty' : 5, 'incoming_rate': 100, 'stock_uom': 'Nos', 'conversion_factor': 1}
]

# Material Issue
mi = [
	{'doctype': 'Stock Entry', 'posting_date': '2012-09-01', 'transfer_date': '2012-09-01', 'posting_time': '14:00', 'company': 'Test Company', 'fiscal_year' : '2012-2013', 'purpose': 'Material Issue', 'name': 'MI001'},
	{'doctype': 'Stock Entry Detail', 'parenttype': 'Stock Entry', 'parentfield' : 'mtn_details', 'parent' : 'MI001', 'name': 'SED004', 'item_code' : 'test_item', 's_warehouse' : 'test_wh1', 'qty' : 4, 'transfer_qty' : 4, 'incoming_rate': 100, 'stock_uom': 'Nos', 'conversion_factor': 1}
]