from __future__ import unicode_literals
import webnotes
from webnotes import _

install_docs = [
	{"doctype":"Role", "role_name":"Material Manager", "name":"Material Manager"},
	{"doctype":"Role", "role_name":"Material Master Manager", "name":"Material Master Manager"},
	{"doctype":"Role", "role_name":"Material User", "name":"Material User"},
	{"doctype":"Role", "role_name":"Quality Manager", "name":"Quality Manager"},
]

@webnotes.whitelist()
def get_projected_qty(item_code=None, warehouse=None):
	if not (item_code and warehouse):
		item_code = webnotes.form_dict.get("item_code")
		warehouse = webnotes.form_dict.get("warehouse")
		
	projected_qty = webnotes.conn.sql("""select ifnull(projected_qty, 0) from `tabBin`
		where item_code=%s and warehouse=%s""", (item_code, warehouse))
	
	return {"projected_qty": projected_qty and projected_qty[0][0] or 0}
	
def validate_end_of_life(item_code, end_of_life=None):
	if not end_of_life:
		end_of_life = webnotes.conn.get_value("Item", item_code, "end_of_life")
	
	from webnotes.utils import getdate, now_datetime, formatdate
	if end_of_life and getdate(end_of_life) > now_datetime().date():
		raise Exception, _("Item: %(item_code)s reached its end of life on %(date)s") % \
			{"item_code": item_code, "date": formatdate(end_of_life)}