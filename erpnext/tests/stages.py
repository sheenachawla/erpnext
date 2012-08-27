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
stages = {
	"Install": {
		"data": [
			"tests.install_test"
		]
	},
	"Setup": {
		"stages": ["Install"],
		"tests": [
			"setup.doctype.setup_control.test_setup_control"
		],
	},
	"Master": {
		"stages": ["Setup"],
		"tests": [
			"stock.doctype.item.test_item",
			"accounts.doctype.account.test_account",
			"accounts.doctype.cost_center.test_cost_center",
			"accounts.doctype.party.test_party",
		],
	},	
	"Accounts": {
		"stages": ["Master"],
		"tests": [
			"accounts.doctype.journal_voucher.test_journal_voucher",
			"accounts.doctype.gl_entry.test_gl_entry",
			"accounts.doctype.payment_entry.test_payment_entry",
		],
	},
	"Buying": {
		"stages": ["Master"],
		"tests": [
			"buying.doctype.purchase_request.test_purchase_request",
		],
	},
	"Selling": {
		"stages": ["Master"],
		"tests": [
			"selling.doctype.sales_order.test_sales_order",
		],
	},
}

import webnotes

committed = []

def upto(stage, with_tests=False):
	"""commit data upto a stage"""
	global committed
	
	# build dependent stages
	stagedata = stages[stage]
	if "stages" in stagedata:
		for reqd_stage in stagedata["stages"]:
			if not reqd_stage in committed:
				upto(reqd_stage, with_tests)
	
	# commit data or test files required for this stage
	if "data" in stagedata:
		for data_module_name in stagedata["data"]:
			module = __import__(data_module_name, fromlist = [data_module_name.split(".")[-1]])
			if hasattr(module, 'load_data'):
				webnotes.conn.begin()
				module.load_data()
				webnotes.conn.commit()
	
	if with_tests:
		test_stage(stage)
	
	# commit data in all test files
	if "tests" in stagedata:
		for test_module_name in stagedata["tests"]:
			module = __import__(test_module_name, fromlist = [test_module_name.split(".")[-1]])
			if hasattr(module, 'load_data'):
				webnotes.conn.begin()
				module.load_data()
				webnotes.conn.commit()
			
	committed.append(stage)

def test_stage(stage):
	"""run a stage"""
	import unittest, conf, sys
	webnotes.connect(conf.test_db_name)
	
	stagedata = stages[stage]
	if not stagedata.get("tests"): return
	def _load_test_suite():
		test_suite = unittest.TestSuite()
		for module in map(lambda module_name: __import__(module_name,
			fromlist = [module_name.split(".")[-1]]), stagedata["tests"]):
			test_suite.addTest(unittest.TestLoader().loadTestsFromModule(module))
		return test_suite
	
	verbosity = 2
	unittest.TextTestRunner(verbosity=verbosity).run(_load_test_suite())