# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd.
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes
import unittest
from website.doctype.shopping_cart_settings.shopping_cart_settings import ShoppingCartSetupError

class TestShoppingCartSettings(unittest.TestCase):
	def setUp(self):
		webnotes.delete_doc("Shopping Cart Settings", "Shopping Cart Settings")

	def get_cart_settings(self):
		return webnotes.bean({"doctype": "Shopping Cart Settings",
			"company": "_Test Company"})
		
	def test_price_list_territory_overlap(self):
		cart_settings = self.get_cart_settings()
		
		def _add_price_list(price_list):
			cart_settings.doclist.append({
				"doctype": "Shopping Cart Price List",
				"parentfield": "price_lists",
				"selling_price_list": price_list
			})
		
		for price_list in ("_Test Price List Rest of the World", "_Test Price List India"):
			_add_price_list(price_list)
		
		controller = cart_settings.make_controller()
		controller.validate_overlapping_territories("price_lists", "selling_price_list")
		
		_add_price_list("_Test Price List 2")
		
		controller = cart_settings.make_controller()
		self.assertRaises(ShoppingCartSetupError, controller.validate_overlapping_territories,
			"price_lists", "selling_price_list")
			
		return cart_settings
		
	def test_taxes_territory_overlap(self):
		cart_settings = self.get_cart_settings()
		
		def _add_tax_master(tax_master):
			cart_settings.doclist.append({
				"doctype": "Shopping Cart Taxes and Charges Master",
				"parentfield": "sales_taxes_and_charges_masters",
				"sales_taxes_and_charges_master": tax_master
			})
		
		for tax_master in ("_Test Sales Taxes and Charges Master", "_Test India Tax Master"):
			_add_tax_master(tax_master)
			
		controller = cart_settings.make_controller()
		controller.validate_overlapping_territories("sales_taxes_and_charges_masters",
			"sales_taxes_and_charges_master")
			
		_add_tax_master("_Test Sales Taxes and Charges Master 2")
		
		controller = cart_settings.make_controller()
		self.assertRaises(ShoppingCartSetupError, controller.validate_overlapping_territories,
			"sales_taxes_and_charges_masters", "sales_taxes_and_charges_master")
		
	def test_exchange_rate_exists(self):
		webnotes.conn.sql("""delete from `tabCurrency Exchange`""")
		
		cart_settings = self.test_price_list_territory_overlap()
		controller = cart_settings.make_controller()
		self.assertRaises(ShoppingCartSetupError, controller.validate_exchange_rates_exist)
		
		from setup.doctype.currency_exchange.test_currency_exchange import test_records as \
			currency_exchange_records
		webnotes.bean(currency_exchange_records[0]).insert()
		controller.validate_exchange_rates_exist()
		
test_records = [
	[
		{
			"doctype": "Shopping Cart Settings",
			"name": "Shopping Cart Settings",
			"company": "_Test Company",
			"default_territory": "_Test Territory Rest of the World",
			"default_customer_group": "_Test Customer Group",
			"quotation_series": "_T-Quotation-"
		},
		{
			"doctype": "Shopping Cart Price List",
			"parentfield": "price_lists",
			"selling_price_list": "_Test Price List Rest of the World"
		},
		{
			"doctype": "Shopping Cart Price List",
			"parentfield": "price_lists",
			"selling_price_list": "_Test Price List India"
		},
		{
			"doctype": "Shopping Cart Shipping Rule",
			"parentfield": "shipping_rules",
			"shipping_rule": "_Test Shipping Rule - _Test Territory"
		},
		{
			"doctype": "Shopping Cart Taxes and Charges Master",
			"parentfield": "sales_taxes_and_charges_masters",
			"sales_taxes_and_charges_master": "_Test Sales Taxes and Charges Master"
		},
		{
			"doctype": "Shopping Cart Taxes and Charges Master",
			"parentfield": "sales_taxes_and_charges_masters",
			"sales_taxes_and_charges_master": "_Test India Tax Master"
		}
	]
]