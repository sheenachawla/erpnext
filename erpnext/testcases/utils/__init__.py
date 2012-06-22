import unittest
import webnotes
from webnotes.utils import cint

class TestBase(unittest.TestCase):
	def setUp(self):
		webnotes.connect()
		webnotes.conn.begin()
		
		import conf
		print '-'*70
		print "Connected to database %s" % conf.db_name
		print "_"*30
		
		
		
	#===========================================================================
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

	#===========================================================================
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
		
		print "Nestedset model properly built for %s" % dt
		
	def create_doc(self, records):
		from startup.install import create_doc
		create_doc(records)	

	def tearDown(self):
		webnotes.conn.rollback()
		webnotes.conn.close()
		print '_'*30
		print "All transactions rolled back and connection closed"
