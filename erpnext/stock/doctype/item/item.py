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

from website.web_page import Page

class DocType(Page):		
	def autoname(self):
		self.doc.name = self.doc.item_code
		
	def validate(self):
		self.no_duplicate('uom_conversion_details', keys=['uom'])
		self.no_duplicate('ref_rate_details', keys=['price_list_name', 'ref_currency'])
		self.no_duplicate('item_tax', keys=['tax_type'])
		Page.validate(self)
	
	def on_update(self):
		Page.on_update(self)

	def on_rename(self,newdn,olddn):
		webnotes.conn.sql("update tabItem set item_code = %s where name = %s", (newdn, olddn))

	def get_tax_rate(self, tax_type):
		rate = webnotes.conn.sql("select tax_rate from tabAccount where name = %s", tax_type)
		return { 'tax_rate'	:	rate and flt(rate[0][0]) or 0 }

	# 
	# def on_update(self):
	# 	"""
	# 	"""
	# 	
	# 	bin = webnotes.conn.sql("select stock_uom from `tabBin` where item_code=%s", 
	# 		self.doc.item_code)
	# 	
	# 	if bin and cstr(bin[0][0]) != cstr(self.doc.stock_uom):
	# 		msgprint("Please Update Stock UOM with the help of Stock UOM Replace Utility.")
	# 		raise Exception
	# 	check_list = []
	# 	for d in getlist(self.doclist,'uom_conversion_details'):
	# 		if not self.doc.stock_uom:
	# 			msgprint("Please enter Stock UOM first.")
	# 			raise Exception
	# 
	# 		if cstr(d.uom) in check_list:
	# 			msgprint("UOM %s has been entered more than once in Conversion Factor Details." % cstr(d.uom))
	# 			raise Exception
	# 		else:
	# 			check_list.append(cstr(d.uom))
	# 
	# 		if cstr(d.uom) == cstr(self.doc.stock_uom):
	# 			if flt(d.conversion_factor) != 1:
	# 				msgprint("Conversion Fator of UOM : %s should be equal to 1. As UOM : %s is Stock UOM of Item: %s." % ( cstr(d.uom), cstr(d.uom), cstr(self.doc.name)))
	# 				raise Exception
	# 			# else set uom_exist as true
	# 			uom_exist='true'
	# 		elif cstr(d.uom) != cstr(self.doc.stock_uom) and flt(d.conversion_factor) == 1:
	# 			msgprint("Conversion Factor of UOM : %s should not be equal to 1. As UOM : %s is not Stock UOM of Item: %s." % ( cstr(d.uom), cstr(d.uom), cstr(self.doc.name)))
	# 			raise Exception
	# 
	# 	if not cstr(self.doc.stock_uom) in check_list :
	# 		child = addchild( self.doc, 'uom_conversion_details', 'UOM Conversion Detail', 1, self.doclist)
	# 		child.uom = self.doc.stock_uom
	# 		child.conversion_factor = 1
	# 		child.save()
	# 
	# 
	# # Check whether Tax Rate is not entered twice for same Tax Type
	# def check_item_tax(self):
	# 	check_list=[]
	# 	for d in getlist(self.doclist,'item_tax'):
	# 		account_type = webnotes.conn.sql("select account_type from tabAccount where name = %s",d.tax_type)
	# 		account_type = account_type and account_type[0][0] or ''
	# 		if account_type not in ['Tax', 'Chargeable']:
	# 			msgprint("'%s' is not Tax / Chargeable Account"%(d.tax_type))
	# 			raise Exception, "Tax Account validation"
	# 		else:
	# 			if d.tax_type in check_list:
	# 				msgprint("Rate is entered twice for Tax : '%s'." % (d.tax_type))
	# 				raise Exception
	# 			else:
	# 				check_list.append(d.tax_type)
	# 
	# def validate_barcode(self):
	# 	if self.doc.barcode:
	# 		duplicate = webnotes.conn.sql("select name from tabItem where barcode = %s and name != %s", (self.doc.barcode, self.doc.name))
	# 		if duplicate:
	# 			msgprint("Barcode: %s already used in item: %s" % (self.doc.barcode, cstr(duplicate[0][0])), raise_exception = 1)
	# 
	# def validate(self):
	# 	fl = {'is_manufactured_item'	:'Is Manufactured Item',
	# 				'is_sub_contracted_item':'Is Sub Contracted Item',
	# 				'is_purchase_item'			:'Is Purchase Item',
	# 				'is_pro_applicable'		 :'Is Pro Applicable'}
	# 	for d in fl:
	# 		if cstr(self.doc.fields[d]) != 'Yes':
	# 			self.check_for_active_boms(check = fl[d])
	# 	self.check_ref_rate_detail()
	# 	self.fill_customer_code()
	# 	self.check_item_tax()
	# 	self.validate_barcode()
	# 	if not self.doc.min_order_qty:
	# 		self.doc.min_order_qty = 0
	# 	self.check_non_asset_warehouse()
	# 
	# 	if self.doc.is_pro_applicable and self.doc.is_pro_applicable == 'Yes' and self.doc.is_manufactured_item and self.doc.is_manufactured_item != 'Yes':
	# 		msgprint("If making Production Order is allowed then, it should also allow to make Bill of Materials. Refer Manufacturing section.")
	# 		raise Exception
	# 
	# 	if self.doc.is_pro_applicable == 'Yes' and self.doc.is_stock_item == 'No':
	# 		msgprint("As Production Order can be made for this Item, then Is Stock Item Should be 'Yes' as we maintain it's stock. Refer Manufacturing and Inventory section.", raise_exception=1)
	# 
	# 	if self.doc.is_stock_item == "Yes" and not self.doc.default_warehouse:
	# 		msgprint("As we maintain stock of this item, its better to maintain default warehouse. To add default warehouse please go to 'Inventory' section. It will be fetched automatically while making Sales Order, Delivery Note, etc.. ", 1)
	# 
	# 	if self.doc.has_serial_no == 'Yes' and self.doc.is_stock_item == 'No':
	# 		msgprint("'Has Serial No' can not be 'Yes' for non-stock item", raise_exception=1)
	# 
	# 	if self.doc.name:
	# 		self.old_page_name = webnotes.conn.get_value('Item', self.doc.name, 'page_name')
	# 			
	# def check_if_sle_exists(self):
	# 	"""
	# 		checks if any stock ledger entry exists for this item
	# 	"""
	# 
	# 	sle = webnotes.conn.sql("select name from `tabStock Ledger Entry` where item_code = %s and ifnull(is_cancelled, 'No') = 'No'", self.doc.name)
	# 	return sle and 'exists' or 'not exists'
	# 
	# 
	# def delete_web_cache(self, page_name):
	# 	import website.web_cache
	# 	website.web_cache.delete_cache(page_name)
	# 
	# def clear_web_cache(self):
	# 	if hasattr(self, 'old_page_name') and self.old_page_name and \
	# 			self.doc.page_name != self.old_page_name:
	# 		self.delete_web_cache(self.doc.page_name)
	# 	
	# 	if self.doc.show_in_website:
	# 		import website.web_cache
	# 		website.web_cache.create_cache(self.doc.page_name, self.doc.doctype, self.doc.name)
	# 		website.web_cache.clear_cache(self.doc.page_name, self.doc.doctype, self.doc.name)
	# 	else:
	# 		self.delete_web_cache(self.doc.page_name)
	# 
	# def update_page_name(self):
	# 	import website.utils
	# 	
	# 	# if same name, do not repeat twice
	# 	if self.doc.name == self.doc.item_name:
	# 		page_name = self.doc.name
	# 	else:
	# 		page_name = self.doc.name + " " + self.doc.item_name
	# 
	# 	self.doc.page_name = website.utils.page_name(page_name)
	# 
	# 	webnotes.conn.set_value('Item', self.doc.name, 'page_name', self.doc.page_name)
	# 
	# 	# no need to check for uniqueness, as name is unique
	# 	
	# def prepare_template_args(self):
	# 	import markdown2
	# 	self.doc.web_description_html = markdown2.markdown(self.doc.description or '',
	# 									extras=["wiki-tables"])
