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
import unittest
import webnotes
from webnotes.utils import cint
from webnotes.model.code import get_obj

class TestBase(unittest.TestCase):
	def setUp(self):
		webnotes.conn.begin()
		
	def assertDoc(self, lst):
		"""assert all values"""
		for d in lst:
			cl, vl = [], []
			for k in d.keys():
				if k!='doctype':
					cl.append('%s=%s' % (k, '%s'))
					vl.append(d[k])

			self.assertTrue(webnotes.conn.sql("select name from `tab%s` \
				where %s limit 1" % (d['doctype'], ' and '.join(cl)), vl))

	def assertCount(self, lst):
		"""assert all values"""
		for d in lst:
			cl, vl = [], []
			for k in d[0].keys():
				if k!='doctype':
					cl.append('%s=%s' % (k, '%s'))
					vl.append(d[0][k])

			self.assertTrue(webnotes.conn.sql("select count(name) from `tab%s` \
				where %s limit 1" % (d[0]['doctype'], ' and '.join(cl)), vl)[0][0] == d[1])

	def assertNsm(self, dt, parent_fld, group_fld):
		# check nested set model
		roots = webnotes.conn.sql("select name, lft, rgt from `tab%s` \
			where ifnull(%s, '') = '' and docstatus < 2" % (dt, parent_fld))
			
		# root's lft, rgt
		for d in roots:
			node_count = webnotes.conn.sql("select count(name) from `tab%s` \
				where lft >= %s and rgt <= %s and docstatus < 2" % (dt, d[1], d[2]))[0][0]
				
			self.assertEqual(cint(d[2]), cint(d[1])+(node_count*2)-1)
			
		# ledger's lft, rgt
		self.assertTrue(webnotes.conn.sql("select name from `tab%s` \
			where ifnull(%s, '') = '%s' and rgt = lft+1" % \
			(dt, group_fld, (group_fld == 'is_group' and 'No' or 'Ledger'))))
				
	def create_docs(self, records, validate=0, on_update=0, make_autoname=1):
		from startup.install import create_doc
		create_doc(records, validate, on_update, make_autoname)	
		
	def submit_doc(self, data, validate=0, on_update=0):
		rec = self.create_docs(data, make_autoname=0)
		rec_obj = get_obj(data[0]['doctype'], data[0]['name'], with_children=1)
		if validate and hasattr(rec_obj, 'validate'):
			rec_obj.validate()
		if on_update and hasattr(rec_obj, 'on_update'):
			rec_obj.on_update()

		rec_obj.on_submit()
		for d in data:
			webnotes.conn.sql("update `tab%s` set docstatus=1 where name = '%s'" % (d['doctype'], d['name']))

		return rec_obj

	def cancel_doc(self, data, validate=0, on_update=0):
		obj = self.submit_doc(data, validate, on_update)
		obj.on_cancel()
		for d in data:
			webnotes.conn.sql("update `tab%s` set docstatus=2 where name = '%s'" % (d['doctype'], d['name']))
		return obj

	def tearDown(self):
		webnotes.conn.rollback()
