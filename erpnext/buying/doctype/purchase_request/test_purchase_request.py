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
from webnotes.tests.test_base import TestBase
from webnotes.utils import now_datetime, add_days

base_purchase_request = {
	"doctype": "Purchase Request",
	"naming_series": "PREQ-",
	"company": "East Wind Corporation",
	"posting_date": now_datetime().date(),
	"__islocal": 1,
}

base_purchase_request_item = {
	"doctype": "Purchase Request Item",
	"parentfield": "purchase_request_items",
	"item_code": "Home Desktop 100",
	"qty": 1,
	"uom": "Nos",
	"schedule_date": add_days(now_datetime().date(), 1),
	"item_name": "Home Desktop 100",
	"description": "Home Desktop 100",
	"__islocal": 1,
	"warehouse": "Default Warehouse"
}


"""
TODO:
# test qty based on previous sales order
# test cancellation if purchase order / supplier quotation already submitted
"""
class TestPurchaseRequest(TestBase):
	def test_create_purchase_request(self):
		prcon = webnotes.model.insert([base_purchase_request,
			base_purchase_request_item])
		
		# check if doclist length is 2
		self.assertEqual(len(webnotes.model.get("Purchase Request", prcon.doc.name)), 2)
		
	def test_submit_purchase_request(self):
		prcon = webnotes.model.get_controller([base_purchase_request,
			base_purchase_request_item])
		prcon.doc.docstatus = 1
		prcon.save()
		
		db_copy = webnotes.model.get("Purchase Request", prcon.doc.name)
		# check if doclist length is 2
		self.assertEqual(len(db_copy), 2)
		# check if docstatus = 1
		self.assertEqual(db_copy[0].docstatus, 1)
		
	def test_create_supplier_quotation(self):
		prcon = webnotes.model.insert([base_purchase_request,
			base_purchase_request_item])
		prcon.doc.docstatus = 1
		prcon.save()
		sqdoclist = webnotes.model.map_doc("Purchase Request", "Supplier Quotation",
			prcon.doc.name)

		# check if parent and item are both mapped
		self.assertEqual(len(sqdoclist), 2)
		
		# in child, check if purchase_request and purchase_request_item field
		# are mapped correctly
		for d in sqdoclist.get({"parentfield": "supplier_quotation_items"}):
			self.assertEqual(d.purchase_request, prcon.doc.name)
			self.assertEqual(len(prcon.doclist.get({"name": d.purchase_request_item})), 1)
		
		sqcon = webnotes.model.get_controller(sqdoclist)
		sqcon.set_default_values()
		sqcon.doc.party = "Robert Smith"
		sqcon.doc.currency = "USD"
		sqcon.save()
		
		# check if parent and child both get saved
		self.assertEqual(len(webnotes.model.get("Supplier Quotation", sqcon.doc.name)), 2)
		
		# check if insert possible
		# output
		# import pprint
		# pprint.pprint(sqcon.doclist)
		
	def test_version(self):
		from datetime import timedelta
		from webnotes.model.versions import get_version, serialize, deserialize, diff
		prcon = webnotes.model.insert([base_purchase_request,
			base_purchase_request_item])
		
		versions = []
		
		# create arbitrary number of records
		for i in xrange(2):
			versions.append([prcon.doc.modified, prcon.doclist.copy()])
			
			import time
			time.sleep(1)
			
			prcon.doc.posting_date = add_days(prcon.doc.posting_date, 1)
			prcon.doclist[1].update({"qty": i+5})
			prcon.add_child(base_purchase_request_item)
			prcon.save()
		
		# test if versions are merged properly
		for v in versions:
			# check if version exists
			self.assertTrue(webnotes.conn.exists("Version",
				{"doc_type": prcon.doc.doctype, "doc_name": prcon.doc.name,
				"doc_modified": v[0]}))
			
			# check if the recreated doclist is same as that one in the versions list
			self.assertEqualDoclist(get_version(prcon.doc.doctype, prcon.doc.name, v[0]),
				v[1], ["modified"])
			
			# check equality after filtering valid fields
			v[1].filter_valid_fields()
			self.assertEqual(get_version(prcon.doc.doctype, prcon.doc.name, v[0]), v[1])