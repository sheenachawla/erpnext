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
import webnotes.model
from webnotes.tests.test_base import TestBase

base_party = {
	"doctype": 'Party', "name": "test_party", "party_type": "Customer",
	"default_currency": "INR", "default_price_list": "Standard", 
	"territory": "Default", "party_group": "Default Party Group"
}

def load_data(session):
	make_party_groups(session)
	make_parties(session)

def make_party_groups(session):
	session.insert({
		"doctype": "Party Group", "name": "Default Party Group"
	})

def make_lead(session):
	session.insert({
		"doctype": "Lead", "name": "LEAD001", "lead_name": "Robert Smith",
		"status": "Open", "naming_series": "LEAD",
		"address_line1": "F/102, 247 Park",
		"mobile_no": "1234567890", "email_id": "email@domain.com",
		"source": "Website", "city": "Test City", "country": "India",
		"phone": "9090909090"
	})

def make_parties(session):
	# make customer and supplier
	parties = [
		{"doctype": "Party", "name": "Robert Smith", "party_type": "Customer and Supplier"}, 
		{"doctype": "Party", "name": "Alpha Corporation", "party_type": "Customer"},
		{"doctype": "Party", "name": "Medern Associates", "party_type": "Supplier"}
	]
	for p in parties:
		session.insert(p)
	
	
class TestParty(TestBase):
	def setUp(self):
		super(TestParty, self).setUp()
		make_party_groups(self.session)
		make_lead(self.session)
		
	def test_party_creation(self):
		self.session.insert(base_party)
		self.assertTrue(self.session.db.exists("Party", "test_party"))
		self.assertTrue(self.session.db.exists("Party", "test_party"))
		
	def test_lead_status(self):
		self.session.insert_variants(base_party, [{'lead_id': 'LEAD001'}])
		self.assertEqual(self.session.db.get_value("Lead", "LEAD001", "status"), "Converted")

	def test_address_and_contact(self):
		self.session.insert_variants(base_party, [{'lead_id': 'LEAD001'}])
		self.assertTrue(
			self.session.db.get_value("Address", {
				"party": "test_party",
				"address_type": "Office",
				"email_id": "email@domain.com",
				"is_primary_address": 1,
				"name": "test_party-Office",
				"city": "Test City",
				"country": "India",
				"phone": "9090909090"
			})
		)
		self.assertTrue(
			self.session.db.get_value("Contact", {
				"party": "test_party",
				"email_id": "email@domain.com",
				"is_primary_contact": 1,
				"first_name": "Robert Smith",
				"name": "Robert Smith-test_party"
			})
		)

	def test_party_deletion(self):
		self.session.insert_variants(base_party, [{'lead_name': 'LEAD001'}])
		self.session.delete_doc('Party', 'test_party')
		
		self.assertFalse(self.session.db.exists("Address", "test_party-Office"))
		self.assertEqual(self.session.db.get_value("Lead", "LEAD001", "status"), "Open")

	def test_party_renaming(self):
		self.session.insert(base_party)

		self.session.rename_doc("Party", "test_party", "test_party_renamed")

		self.assertFalse(self.session.db.exists("Party", "test_part"))
		self.assertTrue(self.session.db.exists("Party", "test_party_renamed"))