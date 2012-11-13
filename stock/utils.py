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

@webnotes.whitelist()
def get_projected_qty(item_code=None, warehouse=None):
	if not (item_code and warehouse):
		item_code = webnotes.form_dict.get("item_code")
		warehouse = webnotes.form_dict.get("warehouse")
		
	projected_qty = webnotes.conn.sql("""select ifnull(projected_qty, 0) from `tabBin`
		where item_code=%s and warehouse=%s""", (item_code, warehouse))
	
	return {"projected_qty": projected_qty and projected_qty[0][0] or 0}
	
def validate_end_of_life(item_code, end_of_life=None, verbose=1):
	if not end_of_life:
		end_of_life = webnotes.conn.get_value("Item", item_code, "end_of_life")
	
	from webnotes.utils import getdate, now_datetime, formatdate
	if end_of_life and getdate(end_of_life) > now_datetime().date():
		msg = (_("Item") + " %(item_code)s: " + _("reached its end of life on") + \
			" %(date)s. " + _("Please check") + ": %(end_of_life_label)s " + \
			"in Item master") % {
				"item_code": item_code,
				"date": formatdate(end_of_life),
				"end_of_life_label": webnotes.get_label("Item", "end_of_life")
			}
		if verbose:
			msgprint(msg, raise_exception=True)
		else:
			raise webnotes.ValidationError, msg
		
@webnotes.whitelist()
def get_actual_qty(item_code=None, warehouse=None, posting_date=None, posting_time=None):
	# to-do
	return