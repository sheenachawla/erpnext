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

def execute():
	print "installing default records"
	set_home_page()
	create_default_roles()
	set_all_roles_to_admin()
	create_default_master_records()
	save_features_setup()
	update_patch_log()
	

def set_home_page():
	"""Set default home page"""
	webnotes.conn.set_value('Control Panel', 'Control Panel', 'home_page', 'desktop')
	
def save_features_setup():
	""" save global defaults and features setup"""
	from webnotes.model.code import get_obj
	flds = ['fs_item_serial_nos', 'fs_item_batch_nos', 'fs_brands', 'fs_item_barcode', 'fs_item_advanced', \
		'fs_packing_details', 'fs_item_group_in_details', 'fs_exports', 'fs_imports', 'fs_discounts', \
		'fs_purchase_discounts', 'fs_after_sales_installations', 'fs_projects', 'fs_sales_extras', \
		'fs_recurring_invoice', 'fs_pos', 'fs_manufacturing', 'fs_quality', 'fs_page_break', 'fs_more_info'
	]
	fs = get_obj('Features Setup', 'Features Setup')
	for f in flds:
		fs.doc.fields[f] = 1
	fs.doc.save()
	fs.validate()

	
def set_all_roles_to_admin():
	"""Set all roles to administrator profile"""
	from webnotes.model.code import get_obj
	prof = get_obj('Profile', 'Administrator')
	get_obj('Setup Control').add_roles(prof.doc)
	
def update_patch_log():
	"""Update patch version and patch log"""
	from webnotes.utils import set_default
	from webnotes.modules import patch_handler
	from patches import patch_list
	
	version = max(patch_list.patch_dict.keys())
	set_default('patch_version', version)
	
	patch_handler.setup()
	for d in patch_list.patch_dict.get(version):
		pm = 'patches.' + version + '.' + d
		patch_handler.update_patch_log(pm)


def create_doc(records, validate=0, on_update=0, make_autoname=1):
	for data in records:
		if data.get('name'):
			if not webnotes.conn.exists(data['doctype'], data.get('name')):
				create_single_doc(data, validate, on_update, make_autoname)
		elif not webnotes.conn.exists(data):
			create_single_doc(data, validate, on_update, make_autoname)

			
def	create_single_doc(data, validate=0, on_update=0, make_autoname=1):
	from webnotes.model.doc import Document
	from webnotes.model.code import get_obj
	
	d = Document(data['doctype'])
	d.fields.update(data)
	d.save(1, make_autoname=make_autoname)
	doc_obj = get_obj(data['doctype'], d.name, with_children=1)
	if validate and hasattr(doc_obj, 'validate'):
		doc_obj.validate()
	if on_update and hasattr(doc_obj, 'on_update'):
		doc_obj.on_update()
	#print 'Created %(doctype)s %(name)s' % d.fields

	
def create_default_roles():
	roles = [
		{"doctype":"Role", "role_name":"Accounts Manager", "name":"Accounts Manager"},
		{"doctype":"Role", "role_name":"Accounts User", "name":"Accounts User"},
		{"doctype":"Role", "role_name":"Purchase Manager", "name":"Purchase Manager"},
		{"doctype":"Role", "role_name":"Purchase User", "name":"Purchase User"},
		{"doctype":"Role", "role_name":"Purchase Master Manager", "name":"Purchase Master Manager"},
		{"doctype":"Role", "role_name":"Supplier", "name":"Supplier"},
		{"doctype":"Role", "role_name":"Employee", "name":"Employee"},
		{"doctype":"Role", "role_name":"HR Manager", "name":"HR Manager"},
		{"doctype":"Role", "role_name":"HR User", "name":"HR User"},
		{"doctype":"Role", "role_name":"Production Manager", "name":"Production Manager"},
		{"doctype":"Role", "role_name":"Production User", "name":"Production User"},
		{"doctype":"Role", "role_name":"Projects User", "name":"Projects User"},
		{"doctype":"Role", "role_name":"Customer", "name":"Customer"},
		{"doctype":"Role", "role_name":"Partner", "name":"Partner"},
		{"doctype":"Role", "role_name":"Sales Manager", "name":"Sales Manager"},
		{"doctype":"Role", "role_name":"Sales Master Manager", "name":"Sales Master Manager"},
		{"doctype":"Role", "role_name":"Sales User", "name":"Sales User"},
		{'doctype':'Role', 'role_name': 'System Manager', 'name': 'System Manager'},
		{'doctype':'Role', 'role_name':'Support Team', 'name':'Support Team'},
		{'doctype':'Role', 'role_name':'Support Manager', 'name':'Support Manager'},
		{'doctype':'Role', 'role_name':'Maintenance User', 'name':'Maintenance User'},
		{'doctype':'Role', 'role_name':'Maintenance Manager', 'name':'Maintenance Manager'},
		{"doctype":"Role", "role_name":"Material Manager", "name":"Material Manager"},
		{"doctype":"Role", "role_name":"Material Master Manager", "name":"Material Master Manager"},
		{"doctype":"Role", "role_name":"Material User", "name":"Material User"},
		{"doctype":"Role", "role_name":"Quality Manager", "name":"Quality Manager"},
		{"doctype":"Role", "role_name":"Blogger", "name":"Blogger"},
		{"doctype":"Role", "role_name":"Website Manager", "name":"Website Manager"}
	]
	webnotes.conn.begin()
	create_doc(roles, validate=1, on_update=1)
	webnotes.conn.commit()
	

def create_default_master_records():
	records = [
		# item group
		{'doctype': 'Item Group', 'item_group_name': 'All Item Groups', 'is_group': 'Yes', 'name': 'All Item Groups', 'parent_item_group': ''},
		{'doctype': 'Item Group', 'item_group_name': 'Default', 'is_group': 'No', 'name': 'Default', 'parent_item_group': 'All Item Groups'},
		
		# deduction type
		{'doctype': 'Deduction Type', 'name': 'Income Tax', 'description': 'Income Tax', 'deduction_name': 'Income Tax'},
		{'doctype': 'Deduction Type', 'name': 'Professional Tax', 'description': 'Professional Tax', 'deduction_name': 'Professional Tax'},
		{'doctype': 'Deduction Type', 'name': 'Provident Fund', 'description': 'Provident fund', 'deduction_name': 'Provident Fund'},
		
		# earning type
		{'doctype': 'Earning Type', 'name': 'Basic', 'description': 'Basic', 'earning_name': 'Basic', 'taxable': 'Yes'},
		{'doctype': 'Earning Type', 'name': 'House Rent Allowance', 'description': 'House Rent Allowance', 'earning_name': 'House Rent Allowance', 'taxable': 'No'},
		
		# expense claim type
		{'doctype': 'Expense Claim Type', 'name': 'Calls', 'expense_type': 'Calls'},
		{'doctype': 'Expense Claim Type', 'name': 'Food', 'expense_type': 'Food'},
		{'doctype': 'Expense Claim Type', 'name': 'Medical', 'expense_type': 'Medical'},
		{'doctype': 'Expense Claim Type', 'name': 'Others', 'expense_type': 'Others'},
		{'doctype': 'Expense Claim Type', 'name': 'Travel', 'expense_type': 'Travel'},
		
		# leave type
		{'doctype': 'Leave Type', 'leave_type_name': 'Casual Leave', 'name': 'Casual Leave', 'is_encash': 1, 'is_carry_forward': 1, 'max_days_allowed': '3', },
		{'doctype': 'Leave Type', 'leave_type_name': 'Compensatory Off', 'name': 'Compensatory Off', 'is_encash': 0, 'is_carry_forward': 0, },
		{'doctype': 'Leave Type', 'leave_type_name': 'Sick Leave', 'name': 'Sick Leave', 'is_encash': 0, 'is_carry_forward': 0, },
		{'doctype': 'Leave Type', 'leave_type_name': 'Privilege Leave', 'name': 'Privilege Leave', 'is_encash': 0, 'is_carry_forward': 0, },
		{'doctype': 'Leave Type', 'leave_type_name': 'Leave Without Pay', 'name': 'Leave Without Pay', 'is_encash': 0, 'is_carry_forward': 0, 'is_lwp':1},
		
		# territory
		{'doctype': 'Territory', 'territory_name': 'All Territories', 'is_group': 'Yes', 'name': 'All Territories', 'parent_territory': ''},
		{'doctype': 'Territory', 'territory_name': 'Default', 'is_group': 'No', 'name': 'Default', 'parent_territory': 'All Territories'},
			
		# customer group
		{'doctype': 'Customer Group', 'customer_group_name': 'All Customer Groups', 'is_group': 'Yes', 	'name': 'All Customer Groups', 'parent_customer_group': ''},
		{'doctype': 'Customer Group', 'customer_group_name': 'Default Customer Group', 'is_group': 'No', 'name': 'Default Customer Group', 'parent_customer_group': 'All Customer Groups'},
			
		# supplier type
		{'doctype': 'Supplier Type', 'name': 'Default Supplier Type', 'supplier_type': 'Default Supplier Type'},
		
		# Price List
		{'doctype': 'Price List', 'name': 'Default Price List', 'price_list_name': 'Default Price List'},
		{'doctype': 'Price List', 'name': 'Standard', 'price_list_name': 'Standard'},
				
		# warehouse type
		{'doctype': 'Warehouse Type', 'name': 'Default Warehouse Type', 'warehouse_type': 'Default Warehouse Type'},
		{'doctype': 'Warehouse Type', 'name': 'Fixed Asset', 'warehouse_type': 'Fixed Asset'},
		{'doctype': 'Warehouse Type', 'name': 'Reserved', 'warehouse_type': 'Reserved'},
		{'doctype': 'Warehouse Type', 'name': 'Rejected', 'warehouse_type': 'Rejected'},
		{'doctype': 'Warehouse Type', 'name': 'Sample', 'warehouse_type': 'Sample'},
		{'doctype': 'Warehouse Type', 'name': 'Stores', 'warehouse_type': 'Stores'},
		{'doctype': 'Warehouse Type', 'name': 'WIP Warehouse', 'warehouse_type': 'WIP Warehouse'},
		
		# warehouse 
		{'doctype': 'Warehouse', 'warehouse_name': 'Default Warehouse', 'name': 'Default Warehouse', 'warehouse_type': 'Default Warehouse Type'},
			
		# Workstation
		{'doctype': 'Workstation', 'name': 'Default Workstation', 'workstation_name': 'Default Workstation'},
		
		# Sales Person
		{'doctype': 'Sales Person', 'name': 'All Sales Persons', 'sales_person_name': 'All Sales Persons'},
		
		# UOM
		{'uom_name': 'Box', 'doctype': 'UOM', 'name': 'Box'}, 
		{'uom_name': 'Ft', 'doctype': 'UOM', 'name': 'Ft'}, 
		{'uom_name': 'Kg', 'doctype': 'UOM', 'name': 'Kg'}, 
		{'uom_name': 'Ltr', 'doctype': 'UOM', 'name': 'Ltr'}, 
		{'uom_name': 'Meter', 'doctype': 'UOM', 'name': 'Meter'}, 
		{'uom_name': 'Mtr', 'doctype': 'UOM', 'name': 'Mtr'}, 
		{'uom_name': 'Nos', 'doctype': 'UOM', 'name': 'Nos'}, 
		{'uom_name': 'Pair', 'doctype': 'UOM', 'name': 'Pair'}, 
		{'uom_name': 'Set', 'doctype': 'UOM', 'name': 'Set'}, 
		{'uom_name': 'T', 'doctype': 'UOM', 'name': 'T'},
		
		# Currency
		{'currency_name': 'AED', 'doctype': 'Currency', 'name': 'AED'}, 
		{'currency_name': 'AFN', 'doctype': 'Currency', 'name': 'AFN'},
		{'currency_name': 'ALL', 'doctype': 'Currency', 'name': 'ALL'}, 
		{'currency_name': 'AMD', 'doctype': 'Currency', 'name': 'AMD'}, 
		{'currency_name': 'ANG', 'doctype': 'Currency', 'name': 'ANG'}, 
		{'currency_name': 'AOA', 'doctype': 'Currency', 'name': 'AOA'}, 
		{'currency_name': 'ARS', 'doctype': 'Currency', 'name': 'ARS'}, 
		{'currency_name': 'AUD', 'doctype': 'Currency', 'name': 'AUD'}, 
		{'currency_name': 'AZN', 'doctype': 'Currency', 'name': 'AZN'}, 
		{'currency_name': 'BAM', 'doctype': 'Currency', 'name': 'BAM'}, 
		{'currency_name': 'BBD', 'doctype': 'Currency', 'name': 'BBD'}, 
		{'currency_name': 'BDT', 'doctype': 'Currency', 'name': 'BDT'}, 
		{'currency_name': 'BGN', 'doctype': 'Currency', 'name': 'BGN'}, 
		{'currency_name': 'BHD', 'doctype': 'Currency', 'name': 'BHD'}, 
		{'currency_name': 'BIF', 'doctype': 'Currency', 'name': 'BIF'}, 
		{'currency_name': 'BMD', 'doctype': 'Currency', 'name': 'BMD'}, 
		{'currency_name': 'BND', 'doctype': 'Currency', 'name': 'BND'}, 
		{'currency_name': 'BOB', 'doctype': 'Currency', 'name': 'BOB'}, 
		{'currency_name': 'BRL', 'doctype': 'Currency', 'name': 'BRL'}, 
		{'currency_name': 'BSD', 'doctype': 'Currency', 'name': 'BSD'}, 
		{'currency_name': 'BTN', 'doctype': 'Currency', 'name': 'BTN'}, 
		{'currency_name': 'BWP', 'doctype': 'Currency', 'name': 'BWP'}, 
		{'currency_name': 'BYR', 'doctype': 'Currency', 'name': 'BYR'}, 
		{'currency_name': 'BZD', 'doctype': 'Currency', 'name': 'BZD'}, 
		{'currency_name': 'CAD', 'doctype': 'Currency', 'name': 'CAD'}, 
		{'currency_name': 'CDF', 'doctype': 'Currency', 'name': 'CDF'}, 
		{'currency_name': 'CFA', 'doctype': 'Currency', 'name': 'CFA'}, 
		{'currency_name': 'CFP', 'doctype': 'Currency', 'name': 'CFP'}, 
		{'currency_name': 'CHF', 'doctype': 'Currency', 'name': 'CHF'}, 
		{'currency_name': 'CLP', 'doctype': 'Currency', 'name': 'CLP'}, 
		{'currency_name': 'CNY', 'doctype': 'Currency', 'name': 'CNY'}, 
		{'currency_name': 'COP', 'doctype': 'Currency', 'name': 'COP'}, 
		{'currency_name': 'CRC', 'doctype': 'Currency', 'name': 'CRC'}, 
		{'currency_name': 'CUC', 'doctype': 'Currency', 'name': 'CUC'}, 
		{'currency_name': 'CZK', 'doctype': 'Currency', 'name': 'CZK'}, 
		{'currency_name': 'DJF', 'doctype': 'Currency', 'name': 'DJF'}, 
		{'currency_name': 'DKK', 'doctype': 'Currency', 'name': 'DKK'}, 
		{'currency_name': 'DOP', 'doctype': 'Currency', 'name': 'DOP'}, 
		{'currency_name': 'DZD', 'doctype': 'Currency', 'name': 'DZD'}, 
		{'currency_name': 'EEK', 'doctype': 'Currency', 'name': 'EEK'}, 
		{'currency_name': 'EGP', 'doctype': 'Currency', 'name': 'EGP'}, 
		{'currency_name': 'ERN', 'doctype': 'Currency', 'name': 'ERN'}, 
		{'currency_name': 'ETB', 'doctype': 'Currency', 'name': 'ETB'}, 
		{'currency_name': 'EUR', 'doctype': 'Currency', 'name': 'EUR'}, 
		{'currency_name': 'FJD', 'doctype': 'Currency', 'name': 'FJD'}, 
		{'currency_name': 'FKP', 'doctype': 'Currency', 'name': 'FKP'}, 
		{'currency_name': 'FMG', 'doctype': 'Currency', 'name': 'FMG'}, 
		{'currency_name': 'GBP', 'doctype': 'Currency', 'name': 'GBP'}, 
		{'currency_name': 'GEL', 'doctype': 'Currency', 'name': 'GEL'}, 
		{'currency_name': 'GHS', 'doctype': 'Currency', 'name': 'GHS'}, 
		{'currency_name': 'GIP', 'doctype': 'Currency', 'name': 'GIP'}, 
		{'currency_name': 'GMD', 'doctype': 'Currency', 'name': 'GMD'}, 
		{'currency_name': 'GNF', 'doctype': 'Currency', 'name': 'GNF'}, 
		{'currency_name': 'GQE', 'doctype': 'Currency', 'name': 'GQE'}, 
		{'currency_name': 'GTQ', 'doctype': 'Currency', 'name': 'GTQ'}, 
		{'currency_name': 'GYD', 'doctype': 'Currency', 'name': 'GYD'}, 
		{'currency_name': 'HKD', 'doctype': 'Currency', 'name': 'HKD'}, 
		{'currency_name': 'HNL', 'doctype': 'Currency', 'name': 'HNL'}, 
		{'currency_name': 'HRK', 'doctype': 'Currency', 'name': 'HRK'}, 
		{'currency_name': 'HTG', 'doctype': 'Currency', 'name': 'HTG'}, 
		{'currency_name': 'HUF', 'doctype': 'Currency', 'name': 'HUF'}, 
		{'currency_name': 'IDR', 'doctype': 'Currency', 'name': 'IDR'}, 
		{'currency_name': 'ILS', 'doctype': 'Currency', 'name': 'ILS'}, 
		{'currency_name': 'INR', 'doctype': 'Currency', 'name': 'INR'}, 
		{'currency_name': 'IQD', 'doctype': 'Currency', 'name': 'IQD'}, 
		{'currency_name': 'IRR', 'doctype': 'Currency', 'name': 'IRR'}, 
		{'currency_name': 'ISK', 'doctype': 'Currency', 'name': 'ISK'}, 
		{'currency_name': 'JMD', 'doctype': 'Currency', 'name': 'JMD'}, 
		{'currency_name': 'JOD', 'doctype': 'Currency', 'name': 'JOD'}, 
		{'currency_name': 'JPY', 'doctype': 'Currency', 'name': 'JPY'}, 
		{'currency_name': 'KES', 'doctype': 'Currency', 'name': 'KES'}, 
		{'currency_name': 'KGS', 'doctype': 'Currency', 'name': 'KGS'}, 
		{'currency_name': 'KHR', 'doctype': 'Currency', 'name': 'KHR'}, 
		{'currency_name': 'KMF', 'doctype': 'Currency', 'name': 'KMF'}, 
		{'currency_name': 'KPW', 'doctype': 'Currency', 'name': 'KPW'}, 
		{'currency_name': 'KRW', 'doctype': 'Currency', 'name': 'KRW'}, 
		{'currency_name': 'KWD', 'doctype': 'Currency', 'name': 'KWD'}, 
		{'currency_name': 'KYD', 'doctype': 'Currency', 'name': 'KYD'}, 
		{'currency_name': 'KZT', 'doctype': 'Currency', 'name': 'KZT'}, 
		{'currency_name': 'LAK', 'doctype': 'Currency', 'name': 'LAK'}, 
		{'currency_name': 'LBP', 'doctype': 'Currency', 'name': 'LBP'}, 
		{'currency_name': 'LKR', 'doctype': 'Currency', 'name': 'LKR'}, 
		{'currency_name': 'LRD', 'doctype': 'Currency', 'name': 'LRD'}, 
		{'currency_name': 'LSL', 'doctype': 'Currency', 'name': 'LSL'}, 
		{'currency_name': 'LTL', 'doctype': 'Currency', 'name': 'LTL'}, 
		{'currency_name': 'LVL', 'doctype': 'Currency', 'name': 'LVL'}, 
		{'currency_name': 'LYD', 'doctype': 'Currency', 'name': 'LYD'}, 
		{'currency_name': 'MAD', 'doctype': 'Currency', 'name': 'MAD'}, 
		{'currency_name': 'MDL', 'doctype': 'Currency', 'name': 'MDL'}, 
		{'currency_name': 'MGA', 'doctype': 'Currency', 'name': 'MGA'}, 
		{'currency_name': 'MKD', 'doctype': 'Currency', 'name': 'MKD'}, 
		{'currency_name': 'MMK', 'doctype': 'Currency', 'name': 'MMK'}, 
		{'currency_name': 'MNT', 'doctype': 'Currency', 'name': 'MNT'}, 
		{'currency_name': 'MOP', 'doctype': 'Currency', 'name': 'MOP'}, 
		{'currency_name': 'MRO', 'doctype': 'Currency', 'name': 'MRO'}, 
		{'currency_name': 'MUR', 'doctype': 'Currency', 'name': 'MUR'}, 
		{'currency_name': 'MVR', 'doctype': 'Currency', 'name': 'MVR'}, 
		{'currency_name': 'MWK', 'doctype': 'Currency', 'name': 'MWK'}, 
		{'currency_name': 'MXN', 'doctype': 'Currency', 'name': 'MXN'}, 
		{'currency_name': 'MYR', 'doctype': 'Currency', 'name': 'MYR'}, 
		{'currency_name': 'MZM', 'doctype': 'Currency', 'name': 'MZM'}, 
		{'currency_name': 'NAD', 'doctype': 'Currency', 'name': 'NAD'}, 
		{'currency_name': 'NGN', 'doctype': 'Currency', 'name': 'NGN'}, 
		{'currency_name': 'NIO', 'doctype': 'Currency', 'name': 'NIO'}, 
		{'currency_name': 'NOK', 'doctype': 'Currency', 'name': 'NOK'}, 
		{'currency_name': 'NPR', 'doctype': 'Currency', 'name': 'NPR'}, 
		{'currency_name': 'NRs', 'doctype': 'Currency', 'name': 'NRs'}, 
		{'currency_name': 'NZD', 'doctype': 'Currency', 'name': 'NZD'}, 
		{'currency_name': 'OMR', 'doctype': 'Currency', 'name': 'OMR'}, 
		{'currency_name': 'PAB', 'doctype': 'Currency', 'name': 'PAB'}, 
		{'currency_name': 'PEN', 'doctype': 'Currency', 'name': 'PEN'}, 
		{'currency_name': 'PGK', 'doctype': 'Currency', 'name': 'PGK'}, 
		{'currency_name': 'PHP', 'doctype': 'Currency', 'name': 'PHP'}, 
		{'currency_name': 'PKR', 'doctype': 'Currency', 'name': 'PKR'}, 
		{'currency_name': 'PLN', 'doctype': 'Currency', 'name': 'PLN'}, 
		{'currency_name': 'PYG', 'doctype': 'Currency', 'name': 'PYG'}, 
		{'currency_name': 'QAR', 'doctype': 'Currency', 'name': 'QAR'}, 
		{'currency_name': 'RMB', 'doctype': 'Currency', 'name': 'RMB'}, 
		{'currency_name': 'RON', 'doctype': 'Currency', 'name': 'RON'}, 
		{'currency_name': 'RSD', 'doctype': 'Currency', 'name': 'RSD'}, 
		{'currency_name': 'RUB', 'doctype': 'Currency', 'name': 'RUB'}, 
		{'currency_name': 'RWF', 'doctype': 'Currency', 'name': 'RWF'}, 
		{'currency_name': 'SAR', 'doctype': 'Currency', 'name': 'SAR'}, 
		{'currency_name': 'SCR', 'doctype': 'Currency', 'name': 'SCR'}, 
		{'currency_name': 'SDG', 'doctype': 'Currency', 'name': 'SDG'}, 
		{'currency_name': 'SDR', 'doctype': 'Currency', 'name': 'SDR'}, 
		{'currency_name': 'SEK', 'doctype': 'Currency', 'name': 'SEK'}, 
		{'currency_name': 'SGD', 'doctype': 'Currency', 'name': 'SGD'}, 
		{'currency_name': 'SHP', 'doctype': 'Currency', 'name': 'SHP'}, 
		{'currency_name': 'SOS', 'doctype': 'Currency', 'name': 'SOS'}, 
		{'currency_name': 'SRD', 'doctype': 'Currency', 'name': 'SRD'}, 
		{'currency_name': 'STD', 'doctype': 'Currency', 'name': 'STD'}, 
		{'currency_name': 'SYP', 'doctype': 'Currency', 'name': 'SYP'}, 
		{'currency_name': 'SZL', 'doctype': 'Currency', 'name': 'SZL'}, 
		{'currency_name': 'THB', 'doctype': 'Currency', 'name': 'THB'}, 
		{'currency_name': 'TJS', 'doctype': 'Currency', 'name': 'TJS'}, 
		{'currency_name': 'TMT', 'doctype': 'Currency', 'name': 'TMT'}, 
		{'currency_name': 'TND', 'doctype': 'Currency', 'name': 'TND'}, 
		{'currency_name': 'TRY', 'doctype': 'Currency', 'name': 'TRY'}, 
		{'currency_name': 'TTD', 'doctype': 'Currency', 'name': 'TTD'}, 
		{'currency_name': 'TWD', 'doctype': 'Currency', 'name': 'TWD'}, 
		{'currency_name': 'TZS', 'doctype': 'Currency', 'name': 'TZS'}, 
		{'currency_name': 'UAE', 'doctype': 'Currency', 'name': 'UAE'}, 
		{'currency_name': 'UAH', 'doctype': 'Currency', 'name': 'UAH'}, 
		{'currency_name': 'UGX', 'doctype': 'Currency', 'name': 'UGX'}, 
		{'currency_name': 'USD', 'doctype': 'Currency', 'name': 'USD'}, 
		{'currency_name': 'UY', 'doctype': 'Currency', 'name': 'UY'}, 
		{'currency_name': 'UZS', 'doctype': 'Currency', 'name': 'UZS'}, 
		{'currency_name': 'VEB', 'doctype': 'Currency', 'name': 'VEB'}, 
		{'currency_name': 'VND', 'doctype': 'Currency', 'name': 'VND'}, 
		{'currency_name': 'VUV', 'doctype': 'Currency', 'name': 'VUV'}, 
		{'currency_name': 'WST', 'doctype': 'Currency', 'name': 'WST'}, 
		{'currency_name': 'XAF', 'doctype': 'Currency', 'name': 'XAF'}, 
		{'currency_name': 'XCD', 'doctype': 'Currency', 'name': 'XCD'}, 
		{'currency_name': 'XDR', 'doctype': 'Currency', 'name': 'XDR'}, 
		{'currency_name': 'XOF', 'doctype': 'Currency', 'name': 'XOF'}, 
		{'currency_name': 'XPF', 'doctype': 'Currency', 'name': 'XPF'}, 
		{'currency_name': 'YEN', 'doctype': 'Currency', 'name': 'YEN'}, 
		{'currency_name': 'YER', 'doctype': 'Currency', 'name': 'YER'}, 
		{'currency_name': 'YTL', 'doctype': 'Currency', 'name': 'YTL'}, 
		{'currency_name': 'ZAR', 'doctype': 'Currency', 'name': 'ZAR'}, 
		{'currency_name': 'ZMK', 'doctype': 'Currency', 'name': 'ZMK'}, 
		{'currency_name': 'ZWR', 'doctype': 'Currency', 'name': 'ZWR'},
		
		# Country
		{'country_name': 'Afghanistan', 'doctype': 'Country', 'name': 'Afghanistan'}, 
		{'country_name': 'Albania', 'doctype': 'Country', 'name': 'Albania'}, 
		{'country_name': 'Algeria', 'doctype': 'Country', 'name': 'Algeria'}, 
		{'country_name': 'Andorra', 'doctype': 'Country', 'name': 'Andorra'}, 
		{'country_name': 'Angola', 'doctype': 'Country', 'name': 'Angola'}, 
		{'country_name': 'Antarctica', 'doctype': 'Country', 'name': 'Antarctica'}, 
		{'country_name': 'Antigua and Barbuda', 'doctype': 'Country', 'name': 'Antigua and Barbuda'}, 
		{'country_name': 'Argentina', 'doctype': 'Country', 'name': 'Argentina'}, 
		{'country_name': 'Armenia', 'doctype': 'Country', 'name': 'Armenia'}, 
		{'country_name': 'Australia', 'doctype': 'Country', 'name': 'Australia'}, 
		{'country_name': 'Austria', 'doctype': 'Country', 'name': 'Austria'}, 
		{'country_name': 'Azerbaijan', 'doctype': 'Country', 'name': 'Azerbaijan'}, 
		{'country_name': 'Bahamas', 'doctype': 'Country', 'name': 'Bahamas'}, 
		{'country_name': 'Bahrain', 'doctype': 'Country', 'name': 'Bahrain'}, 
		{'country_name': 'Bangladesh', 'doctype': 'Country', 'name': 'Bangladesh'}, 
		{'country_name': 'Barbados', 'doctype': 'Country', 'name': 'Barbados'}, 
		{'country_name': 'Belarus', 'doctype': 'Country', 'name': 'Belarus'}, 
		{'country_name': 'Belgium', 'doctype': 'Country', 'name': 'Belgium'}, 
		{'country_name': 'Belize', 'doctype': 'Country', 'name': 'Belize'}, 
		{'country_name': 'Benin', 'doctype': 'Country', 'name': 'Benin'}, 
		{'country_name': 'Bermuda', 'doctype': 'Country', 'name': 'Bermuda'}, 
		{'country_name': 'Bhutan', 'doctype': 'Country', 'name': 'Bhutan'}, 
		{'country_name': 'Bolivia', 'doctype': 'Country', 'name': 'Bolivia'}, 
		{'country_name': 'Bosnia and Herzegovina', 'doctype': 'Country', 'name': 'Bosnia and Herzegovina'}, 
		{'country_name': 'Botswana', 'doctype': 'Country', 'name': 'Botswana'}, 
		{'country_name': 'Brazil', 'doctype': 'Country', 'name': 'Brazil'}, 
		{'country_name': 'Brunei', 'doctype': 'Country', 'name': 'Brunei'}, 
		{'country_name': 'Bulgaria', 'doctype': 'Country', 'name': 'Bulgaria'}, 
		{'country_name': 'Burkina Faso', 'doctype': 'Country', 'name': 'Burkina Faso'}, 
		{'country_name': 'Burma', 'doctype': 'Country', 'name': 'Burma'}, 
		{'country_name': 'Burundi', 'doctype': 'Country', 'name': 'Burundi'}, 
		{'country_name': 'Cambodia', 'doctype': 'Country', 'name': 'Cambodia'}, 
		{'country_name': 'Cameroon', 'doctype': 'Country', 'name': 'Cameroon'}, 
		{'country_name': 'Canada', 'doctype': 'Country', 'name': 'Canada'}, 
		{'country_name': 'Cape Verde', 'doctype': 'Country', 'name': 'Cape Verde'}, 
		{'country_name': 'Central African Republic', 'doctype': 'Country', 'name': 'Central African Republic'}, 
		{'country_name': 'Chad', 'doctype': 'Country', 'name': 'Chad'}, 
		{'country_name': 'Chile', 'doctype': 'Country', 'name': 'Chile'}, 
		{'country_name': 'China', 'doctype': 'Country', 'name': 'China'}, 
		{'country_name': 'Colombia', 'doctype': 'Country', 'name': 'Colombia'}, 
		{'country_name': 'Comoros', 'doctype': 'Country', 'name': 'Comoros'}, 
		{'country_name': 'Congo, Democratic Republic', 'doctype': 'Country', 'name': 'Congo, Democratic Republic'}, 
		{'country_name': 'Congo, Republic of the', 'doctype': 'Country', 'name': 'Congo, Republic of the'}, 
		{'country_name': 'Costa Rica', 'doctype': 'Country', 'name': 'Costa Rica'}, 
		{'country_name': 'Cote dIvoire', 'doctype': 'Country', 'name': 'Cote dIvoire'}, 
		{'country_name': 'Croatia', 'doctype': 'Country', 'name': 'Croatia'}, 
		{'country_name': 'Cuba', 'doctype': 'Country', 'name': 'Cuba'}, 
		{'country_name': 'Cyprus', 'doctype': 'Country', 'name': 'Cyprus'}, 
		{'country_name': 'Czech Republic', 'doctype': 'Country', 'name': 'Czech Republic'}, 
		{'country_name': 'Denmark', 'doctype': 'Country', 'name': 'Denmark'}, 
		{'country_name': 'Djibouti', 'doctype': 'Country', 'name': 'Djibouti'}, 
		{'country_name': 'Dominica', 'doctype': 'Country', 'name': 'Dominica'}, 
		{'country_name': 'Dominican Republic', 'doctype': 'Country', 'name': 'Dominican Republic'}, 
		{'country_name': 'East Timor', 'doctype': 'Country', 'name': 'East Timor'}, 
		{'country_name': 'Ecuador', 'doctype': 'Country', 'name': 'Ecuador'}, 
		{'country_name': 'Egypt', 'doctype': 'Country', 'name': 'Egypt'}, 
		{'country_name': 'El Salvador', 'doctype': 'Country', 'name': 'El Salvador'}, 
		{'country_name': 'Equatorial Guinea', 'doctype': 'Country', 'name': 'Equatorial Guinea'}, 
		{'country_name': 'Eritrea', 'doctype': 'Country', 'name': 'Eritrea'}, 
		{'country_name': 'Estonia', 'doctype': 'Country', 'name': 'Estonia'}, 
		{'country_name': 'Ethiopia', 'doctype': 'Country', 'name': 'Ethiopia'}, 
		{'country_name': 'Fiji', 'doctype': 'Country', 'name': 'Fiji'}, 
		{'country_name': 'Finland', 'doctype': 'Country', 'name': 'Finland'}, 
		{'country_name': 'France', 'doctype': 'Country', 'name': 'France'}, 
		{'country_name': 'Gabon', 'doctype': 'Country', 'name': 'Gabon'}, 
		{'country_name': 'Gambia', 'doctype': 'Country', 'name': 'Gambia'}, 
		{'country_name': 'Georgia', 'doctype': 'Country', 'name': 'Georgia'}, 
		{'country_name': 'Germany', 'doctype': 'Country', 'name': 'Germany'}, 
		{'country_name': 'Ghana', 'doctype': 'Country', 'name': 'Ghana'}, 
		{'country_name': 'Greece', 'doctype': 'Country', 'name': 'Greece'}, 
		{'country_name': 'Greenland', 'doctype': 'Country', 'name': 'Greenland'}, 
		{'country_name': 'Grenada', 'doctype': 'Country', 'name': 'Grenada'}, 
		{'country_name': 'Guatemala', 'doctype': 'Country', 'name': 'Guatemala'}, 
		{'country_name': 'Guinea', 'doctype': 'Country', 'name': 'Guinea'}, 
		{'country_name': 'Guinea-Bissa', 'doctype': 'Country', 'name': 'Guinea-Bissa'}, 
		{'country_name': 'Guyana', 'doctype': 'Country', 'name': 'Guyana'}, 
		{'country_name': 'Haiti', 'doctype': 'Country', 'name': 'Haiti'}, 
		{'country_name': 'Honduras', 'doctype': 'Country', 'name': 'Honduras'}, 
		{'country_name': 'Hong Kong', 'doctype': 'Country', 'name': 'Hong Kong'}, 
		{'country_name': 'Hungary', 'doctype': 'Country', 'name': 'Hungary'}, 
		{'country_name': 'Iceland', 'doctype': 'Country', 'name': 'Iceland'}, 
		{'country_name': 'India', 'doctype': 'Country', 'name': 'India'}, 
		{'country_name': 'Indonesia', 'doctype': 'Country', 'name': 'Indonesia'}, 
		{'country_name': 'Iran', 'doctype': 'Country', 'name': 'Iran'}, 
		{'country_name': 'Iraq', 'doctype': 'Country', 'name': 'Iraq'}, 
		{'country_name': 'Ireland', 'doctype': 'Country', 'name': 'Ireland'}, 
		{'country_name': 'Israel', 'doctype': 'Country', 'name': 'Israel'}, 
		{'country_name': 'Italy', 'doctype': 'Country', 'name': 'Italy'}, 
		{'country_name': 'Jamaica', 'doctype': 'Country', 'name': 'Jamaica'}, 
		{'country_name': 'Japan', 'doctype': 'Country', 'name': 'Japan'}, 
		{'country_name': 'Jordan', 'doctype': 'Country', 'name': 'Jordan'}, 
		{'country_name': 'Kazakhstan', 'doctype': 'Country', 'name': 'Kazakhstan'}, 
		{'country_name': 'Kenya', 'doctype': 'Country', 'name': 'Kenya'}, 
		{'country_name': 'Kiribati', 'doctype': 'Country', 'name': 'Kiribati'}, 
		{'country_name': 'Korea, North', 'doctype': 'Country', 'name': 'Korea, North'}, 
		{'country_name': 'Korea, South', 'doctype': 'Country', 'name': 'Korea, South'}, 
		{'country_name': 'Kuwait', 'doctype': 'Country', 'name': 'Kuwait'}, 
		{'country_name': 'Kyrgyzstan', 'doctype': 'Country', 'name': 'Kyrgyzstan'}, 
		{'country_name': 'Laos', 'doctype': 'Country', 'name': 'Laos'}, 
		{'country_name': 'Latvia', 'doctype': 'Country', 'name': 'Latvia'}, 
		{'country_name': 'Lebanon', 'doctype': 'Country', 'name': 'Lebanon'}, 
		{'country_name': 'Lesotho', 'doctype': 'Country', 'name': 'Lesotho'}, 
		{'country_name': 'Liberia', 'doctype': 'Country', 'name': 'Liberia'}, 
		{'country_name': 'Libya', 'doctype': 'Country', 'name': 'Libya'}, 
		{'country_name': 'Liechtenstein', 'doctype': 'Country', 'name': 'Liechtenstein'}, 
		{'country_name': 'Lithuania', 'doctype': 'Country', 'name': 'Lithuania'}, 
		{'country_name': 'Luxembourg', 'doctype': 'Country', 'name': 'Luxembourg'}, 
		{'country_name': 'Macedonia', 'doctype': 'Country', 'name': 'Macedonia'}, 
		{'country_name': 'Madagascar', 'doctype': 'Country', 'name': 'Madagascar'}, 
		{'country_name': 'Malawi', 'doctype': 'Country', 'name': 'Malawi'}, 
		{'country_name': 'Malaysia', 'doctype': 'Country', 'name': 'Malaysia'}, 
		{'country_name': 'Maldives', 'doctype': 'Country', 'name': 'Maldives'}, 
		{'country_name': 'Mali', 'doctype': 'Country', 'name': 'Mali'}, 
		{'country_name': 'Malta', 'doctype': 'Country', 'name': 'Malta'}, 
		{'country_name': 'Marshall Islands', 'doctype': 'Country', 'name': 'Marshall Islands'}, 
		{'country_name': 'Mauritania', 'doctype': 'Country', 'name': 'Mauritania'}, 
		{'country_name': 'Mauritius', 'doctype': 'Country', 'name': 'Mauritius'}, 
		{'country_name': 'Mexico', 'doctype': 'Country', 'name': 'Mexico'}, 
		{'country_name': 'Micronesia', 'doctype': 'Country', 'name': 'Micronesia'}, 
		{'country_name': 'Moldova', 'doctype': 'Country', 'name': 'Moldova'}, 
		{'country_name': 'Monaco', 'doctype': 'Country', 'name': 'Monaco'}, 
		{'country_name': 'Mongolia', 'doctype': 'Country', 'name': 'Mongolia'}, 
		{'country_name': 'Morocco', 'doctype': 'Country', 'name': 'Morocco'}, 
		{'country_name': 'Mozambique', 'doctype': 'Country', 'name': 'Mozambique'}, 
		{'country_name': 'Namibia', 'doctype': 'Country', 'name': 'Namibia'}, 
		{'country_name': 'Naur', 'doctype': 'Country', 'name': 'Naur'}, 
		{'country_name': 'Nepal', 'doctype': 'Country', 'name': 'Nepal'}, 
		{'country_name': 'Netherlands', 'doctype': 'Country', 'name': 'Netherlands'}, 
		{'country_name': 'New Zealand', 'doctype': 'Country', 'name': 'New Zealand'}, 
		{'country_name': 'Nicaragua', 'doctype': 'Country', 'name': 'Nicaragua'}, 
		{'country_name': 'Niger', 'doctype': 'Country', 'name': 'Niger'}, 
		{'country_name': 'Nigeria', 'doctype': 'Country', 'name': 'Nigeria'}, 
		{'country_name': 'North Korea', 'doctype': 'Country', 'name': 'North Korea'}, 
		{'country_name': 'Norway', 'doctype': 'Country', 'name': 'Norway'}, 
		{'country_name': 'Oman', 'doctype': 'Country', 'name': 'Oman'}, 
		{'country_name': 'Pakistan', 'doctype': 'Country', 'name': 'Pakistan'}, 
		{'country_name': 'Panama', 'doctype': 'Country', 'name': 'Panama'}, 
		{'country_name': 'Papua New Guinea', 'doctype': 'Country', 'name': 'Papua New Guinea'}, 
		{'country_name': 'Paraguay', 'doctype': 'Country', 'name': 'Paraguay'}, 
		{'country_name': 'Per', 'doctype': 'Country', 'name': 'Per'}, 
		{'country_name': 'Philippines', 'doctype': 'Country', 'name': 'Philippines'}, 
		{'country_name': 'Poland', 'doctype': 'Country', 'name': 'Poland'}, 
		{'country_name': 'Portugal', 'doctype': 'Country', 'name': 'Portugal'}, 
		{'country_name': 'Qatar', 'doctype': 'Country', 'name': 'Qatar'}, 
		{'country_name': 'Romania', 'doctype': 'Country', 'name': 'Romania'}, 
		{'country_name': 'Russia', 'doctype': 'Country', 'name': 'Russia'}, 
		{'country_name': 'Rwanda', 'doctype': 'Country', 'name': 'Rwanda'}, 
		{'country_name': 'Samoa', 'doctype': 'Country', 'name': 'Samoa'}, 
		{'country_name': 'San Marino', 'doctype': 'Country', 'name': 'San Marino'}, 
		{'country_name': ' Sao Tome', 'doctype': 'Country', 'name': 'Sao Tome'}, 
		{'country_name': 'Saudi Arabia', 'doctype': 'Country', 'name': 'Saudi Arabia'}, 
		{'country_name': 'Senegal', 'doctype': 'Country', 'name': 'Senegal'}, 
		{'country_name': 'Serbia and Montenegro', 'doctype': 'Country', 'name': 'Serbia and Montenegro'}, 
		{'country_name': 'Seychelles', 'doctype': 'Country', 'name': 'Seychelles'}, 
		{'country_name': 'Sierra Leone', 'doctype': 'Country', 'name': 'Sierra Leone'}, 
		{'country_name': 'Singapore', 'doctype': 'Country', 'name': 'Singapore'}, 
		{'country_name': 'Slovakia', 'doctype': 'Country', 'name': 'Slovakia'}, 
		{'country_name': 'Slovenia', 'doctype': 'Country', 'name': 'Slovenia'}, 
		{'country_name': 'Solomon Islands', 'doctype': 'Country', 'name': 'Solomon Islands'}, 
		{'country_name': 'Somalia', 'doctype': 'Country', 'name': 'Somalia'}, 
		{'country_name': 'South Africa', 'doctype': 'Country', 'name': 'South Africa'}, 
		{'country_name': 'South Korea', 'doctype': 'Country', 'name': 'South Korea'}, 
		{'country_name': 'Spain', 'doctype': 'Country', 'name': 'Spain'}, 
		{'country_name': 'Sri Lanka', 'doctype': 'Country', 'name': 'Sri Lanka'}, 
		{'country_name': 'Sudan', 'doctype': 'Country', 'name': 'Sudan'}, 
		{'country_name': 'Suriname', 'doctype': 'Country', 'name': 'Suriname'}, 
		{'country_name': 'Swaziland', 'doctype': 'Country', 'name': 'Swaziland'}, 
		{'country_name': 'Sweden', 'doctype': 'Country', 'name': 'Sweden'}, 
		{'country_name': 'Switzerland', 'doctype': 'Country', 'name': 'Switzerland'}, 
		{'country_name': 'Syria', 'doctype': 'Country', 'name': 'Syria'}, 
		{'country_name': 'Taiwan', 'doctype': 'Country', 'name': 'Taiwan'}, 
		{'country_name': 'Tajikistan', 'doctype': 'Country', 'name': 'Tajikistan'}, 
		{'country_name': 'Tanzania', 'doctype': 'Country', 'name': 'Tanzania'}, 
		{'country_name': 'Thailand', 'doctype': 'Country', 'name': 'Thailand'}, 
		{'country_name': 'Togo', 'doctype': 'Country', 'name': 'Togo'}, 
		{'country_name': 'Tonga', 'doctype': 'Country', 'name': 'Tonga'}, 
		{'country_name': 'Trinidad and Tobago', 'doctype': 'Country', 'name': 'Trinidad and Tobago'}, 
		{'country_name': 'Tunisia', 'doctype': 'Country', 'name': 'Tunisia'}, 
		{'country_name': 'Turkey', 'doctype': 'Country', 'name': 'Turkey'}, 
		{'country_name': 'Turkmenistan', 'doctype': 'Country', 'name': 'Turkmenistan'}, 
		{'country_name': 'Uganda', 'doctype': 'Country', 'name': 'Uganda'}, 
		{'country_name': 'Ukraine', 'doctype': 'Country', 'name': 'Ukraine'}, 
		{'country_name': 'United Arab Emirates', 'doctype': 'Country', 'name': 'United Arab Emirates'}, 
		{'country_name': 'United Kingdom', 'doctype': 'Country', 'name': 'United Kingdom'}, 
		{'country_name': 'United States', 'doctype': 'Country', 'name': 'United States'}, 
		{'country_name': 'Uruguay', 'doctype': 'Country', 'name': 'Uruguay'}, 
		{'country_name': 'Uzbekistan', 'doctype': 'Country', 'name': 'Uzbekistan'}, 
		{'country_name': 'Vanuat', 'doctype': 'Country', 'name': 'Vanuat'}, 
		{'country_name': 'Venezuela', 'doctype': 'Country', 'name': 'Venezuela'}, 
		{'country_name': 'Vietnam', 'doctype': 'Country', 'name': 'Vietnam'}, 
		{'country_name': 'Yemen', 'doctype': 'Country', 'name': 'Yemen'}, 
		{'country_name': 'Zambia', 'doctype': 'Country', 'name': 'Zambia'}, 
		{'country_name': 'Zimbabwe', 'doctype': 'Country', 'name': 'Zimbabwe'},
		
		# State
		{'state_name': 'Alabama', 'country': 'United States', 'doctype': 'State', 'name': 'Alabama'}, 
		{'state_name': 'Alaska', 'country': 'United States', 'doctype': 'State', 'name': 'Alaska'}, 
		{'state_name': 'Andaman and Nicobar Islands', 'country': 'India', 'doctype': 'State', 'name': 'Andaman and Nicobar Islands'}, 
		{'state_name': 'Andhra Pradesh', 'country': 'India', 'doctype': 'State', 'name': 'Andhra Pradesh'}, 
		{'state_name': 'Arizona', 'country': 'United States', 'doctype': 'State', 'name': 'Arizona'}, 
		{'state_name': 'Arkansas', 'country': 'United States', 'doctype': 'State', 'name': 'Arkansas'}, 
		{'state_name': 'Arunachal Pradesh', 'country': 'India', 'doctype': 'State', 'name': 'Arunachal Pradesh'}, 
		{'state_name': 'Assam', 'country': 'India', 'doctype': 'State', 'name': 'Assam'}, 
		{'state_name': 'Beijing ', 'country': 'China', 'doctype': 'State', 'name': 'Beijing'}, 
		{'state_name': 'Bihar', 'country': 'India', 'doctype': 'State', 'name': 'Bihar'}, 
		{'state_name': 'California', 'country': 'United States', 'doctype': 'State', 'name': 'California'}, 
		{'state_name': 'Chandigarh', 'country': 'India', 'doctype': 'State', 'name': 'Chandigarh'}, 
		{'state_name': 'Changchun ', 'country': 'China', 'doctype': 'State', 'name': 'Changchun'}, 
		{'state_name': 'Chengde', 'country': 'China', 'doctype': 'State', 'name': 'Chengde'}, 
		{'state_name': 'Chengdu', 'country': 'China', 'doctype': 'State', 'name': 'Chengdu'}, 
		{'state_name': 'Chhattisgarh', 'country': 'India', 'doctype': 'State', 'name': 'Chhattisgarh'}, 
		{'state_name': 'Chongqing ', 'country': 'China', 'doctype': 'State', 'name': 'Chongqing'}, 
		{'state_name': 'Colorado', 'country': 'United States', 'doctype': 'State', 'name': 'Colorado'}, 
		{'state_name': 'Connecticut', 'country': 'United States', 'doctype': 'State', 'name': 'Connecticut'}, 
		{'state_name': 'Dadra and Nagar Haveli', 'country': 'India', 'doctype': 'State', 'name': 'Dadra and Nagar Haveli'}, 
		{'state_name': 'Dalian', 'country': 'China', 'doctype': 'State', 'name': 'Dalian'}, 
		{'state_name': 'Daman and Di', 'country': 'India', 'doctype': 'State', 'name': 'Daman and Di'}, 
		{'state_name': 'Delaware', 'country': 'United States', 'doctype': 'State', 'name': 'Delaware'}, 
		{'state_name': 'Delhi', 'country': 'India', 'doctype': 'State', 'name': 'Delhi'}, 
		{'state_name': 'Dongguan ', 'country': 'China', 'doctype': 'State', 'name': 'Dongguan'}, 
		{'state_name': 'Dunhuang ', 'country': 'China', 'doctype': 'State', 'name': 'Dunhuang'}, 
		{'state_name': 'Florida', 'country': 'United States', 'doctype': 'State', 'name': 'Florida'}, 
		{'state_name': 'Georgia', 'country': 'United States', 'doctype': 'State', 'name': 'Georgia'}, 
		{'state_name': 'Goa', 'country': 'India', 'doctype': 'State', 'name': 'Goa'}, 
		{'state_name': 'Guangzho', 'country': 'China', 'doctype': 'State', 'name': 'Guangzho'}, 
		{'state_name': 'Guilin ', 'country': 'China', 'doctype': 'State', 'name': 'Guilin'}, 
		{'state_name': 'Gujarat', 'country': 'India', 'doctype': 'State', 'name': 'Gujarat'}, 
		{'state_name': 'Hangzhou', 'country': 'China', 'doctype': 'State', 'name': 'Hangzhou'}, 
		{'state_name': 'Harbin', 'country': 'China', 'doctype': 'State', 'name': 'Harbin'}, 
		{'state_name': 'Haryana', 'country': 'India', 'doctype': 'State', 'name': 'Haryana'}, 
		{'state_name': 'Hawaii', 'country': 'United States', 'doctype': 'State', 'name': 'Hawaii'}, 
		{'state_name': 'Hefei ', 'country': 'China', 'doctype': 'State', 'name': 'Hefei'}, 
		{'state_name': 'Himachal Pradesh', 'country': 'India', 'doctype': 'State', 'name': 'Himachal Pradesh'}, 
		{'state_name': 'Idaho', 'country': 'United States', 'doctype': 'State', 'name': 'Idaho'}, 
		{'state_name': 'Illinois', 'country': 'United States', 'doctype': 'State', 'name': 'Illinois'}, 
		{'state_name': 'Indiana', 'country': 'United States', 'doctype': 'State', 'name': 'Indiana'}, 
		{'state_name': 'Iowa', 'country': 'United States', 'doctype': 'State', 'name': 'Iowa'}, 
		{'state_name': 'Jammu and Kashmir', 'country': 'India', 'doctype': 'State', 'name': 'Jammu and Kashmir'}, 
		{'state_name': 'Jharkhand', 'country': 'India', 'doctype': 'State', 'name': 'Jharkhand'}, 
		{'state_name': 'Jinan ', 'country': 'China', 'doctype': 'State', 'name': 'Jinan'}, 
		{'state_name': 'Kansas', 'country': 'United States', 'doctype': 'State', 'name': 'Kansas'}, 
		{'state_name': 'Karnataka', 'country': 'India', 'doctype': 'State', 'name': 'Karnataka'}, 
		{'state_name': 'Kashi', 'country': 'China', 'doctype': 'State', 'name': 'Kashi'}, 
		{'state_name': 'Kentucky', 'country': 'United States', 'doctype': 'State', 'name': 'Kentucky'}, 
		{'state_name': 'Kerala', 'country': 'India', 'doctype': 'State', 'name': 'Kerala'}, 
		{'state_name': 'Kowloon ', 'country': 'China', 'doctype': 'State', 'name': 'Kowloon'}, 
		{'state_name': 'Kunming ', 'country': 'China', 'doctype': 'State', 'name': 'Kunming'}, 
		{'state_name': 'Lakshadweep', 'country': 'India', 'doctype': 'State', 'name': 'Lakshadweep'}, 
		{'state_name': 'Lanzho', 'country': 'China', 'doctype': 'State', 'name': 'Lanzho'}, 
		{'state_name': 'Lijiang City ', 'country': 'China', 'doctype': 'State', 'name': 'Lijiang City'}, 
		{'state_name': 'Louisiana', 'country': 'United States', 'doctype': 'State', 'name': 'Louisiana'}, 
		{'state_name': 'Madhya Pradesh', 'country': 'India', 'doctype': 'State', 'name': 'Madhya Pradesh'}, 
		{'state_name': 'Maharashtra', 'country': 'India', 'doctype': 'State', 'name': 'Maharashtra'}, 
		{'state_name': 'Maine', 'country': 'United States', 'doctype': 'State', 'name': 'Maine'}, 
		{'state_name': 'Manipur', 'country': 'India', 'doctype': 'State', 'name': 'Manipur'}, 
		{'state_name': 'Maryland', 'country': 'United States', 'doctype': 'State', 'name': 'Maryland'}, 
		{'state_name': 'Massachusetts', 'country': 'United States', 'doctype': 'State', 'name': 'Massachusetts'}, 
		{'state_name': 'Meghalaya', 'country': 'India', 'doctype': 'State', 'name': 'Meghalaya'}, 
		{'state_name': 'Michigan', 'country': 'United States', 'doctype': 'State', 'name': 'Michigan'}, 
		{'state_name': 'Minnesota', 'country': 'United States', 'doctype': 'State', 'name': 'Minnesota'}, 
		{'state_name': 'Mississippi', 'country': 'United States', 'doctype': 'State', 'name': 'Mississippi'}, 
		{'state_name': 'Missouri', 'country': 'United States', 'doctype': 'State', 'name': 'Missouri'}, 
		{'state_name': 'Mizoram', 'country': 'India', 'doctype': 'State', 'name': 'Mizoram'}, 
		{'state_name': 'Montana', 'country': 'United States', 'doctype': 'State', 'name': 'Montana'}, 
		{'state_name': 'Nagaland', 'country': 'India', 'doctype': 'State', 'name': 'Nagaland'}, 
		{'state_name': 'Nanchang ', 'country': 'China', 'doctype': 'State', 'name': 'Nanchang'}, 
		{'state_name': 'Nanjing', 'country': 'China', 'doctype': 'State', 'name': 'Nanjing'}, 
		{'state_name': 'Nebraska', 'country': 'United States', 'doctype': 'State', 'name': 'Nebraska'}, 
		{'state_name': 'Nevada', 'country': 'United States', 'doctype': 'State', 'name': 'Nevada'}, 
		{'state_name': 'New Hampshire', 'country': 'United States', 'doctype': 'State', 'name': 'New Hampshire'}, 
		{'state_name': 'New Jersey', 'country': 'United States', 'doctype': 'State', 'name': 'New Jersey'}, 
		{'state_name': 'New Mexico', 'country': 'United States', 'doctype': 'State', 'name': 'New Mexico'}, 
		{'state_name': 'New York', 'country': 'United States', 'doctype': 'State', 'name': 'New York'}, 
		{'state_name': 'Ningbo ', 'country': 'China', 'doctype': 'State', 'name': 'Ningbo'}, 
		{'state_name': 'North Carolina', 'country': 'United States', 'doctype': 'State', 'name': 'North Carolina'}, 
		{'state_name': 'North Dakota', 'country': 'United States', 'doctype': 'State', 'name': 'North Dakota'}, 
		{'state_name': 'Ohio', 'country': 'United States', 'doctype': 'State', 'name': 'Ohio'}, 
		{'state_name': 'Oklahoma', 'country': 'United States', 'doctype': 'State', 'name': 'Oklahoma'}, 
		{'state_name': 'Oregon', 'country': 'United States', 'doctype': 'State', 'name': 'Oregon'}, 
		{'state_name': 'Orissa', 'country': 'India', 'doctype': 'State', 'name': 'Orissa'}, 
		{'state_name': 'Pennsylvania', 'country': 'United States', 'doctype': 'State', 'name': 'Pennsylvania'}, 
		{'state_name': 'Puducherry', 'country': 'India', 'doctype': 'State', 'name': 'Puducherry'}, 
		{'state_name': 'Punjab', 'country': 'India', 'doctype': 'State', 'name': 'Punjab'}, 
		{'state_name': 'Qingdao ', 'country': 'China', 'doctype': 'State', 'name': 'Qingdao'}, 
		{'state_name': 'Quf', 'country': 'China', 'doctype': 'State', 'name': 'Quf'}, 
		{'state_name': 'Rajasthan', 'country': 'India', 'doctype': 'State', 'name': 'Rajasthan'}, 
		{'state_name': 'Rhode Island', 'country': 'United States', 'doctype': 'State', 'name': 'Rhode Island'}, 
		{'state_name': 'Sanya ', 'country': 'China', 'doctype': 'State', 'name': 'Sanya'}, 
		{'state_name': 'Shanghai ', 'country': 'China', 'doctype': 'State', 'name': 'Shanghai'}, 
		{'state_name': 'Shenyang', 'country': 'China', 'doctype': 'State', 'name': 'Shenyang'}, 
		{'state_name': 'Shenzhen', 'country': 'China', 'doctype': 'State', 'name': 'Shenzhen'}, 
		{'state_name': 'Sikkim', 'country': 'India', 'doctype': 'State', 'name': 'Sikkim'}, 
		{'state_name': 'South Carolina', 'country': 'United States', 'doctype': 'State', 'name': 'South Carolina'}, 
		{'state_name': 'South Dakota', 'country': 'United States', 'doctype': 'State', 'name': 'South Dakota'}, 
		{'state_name': 'Suzho', 'country': 'China', 'doctype': 'State', 'name': 'Suzho'}, 
		{'state_name': 'Tamil Nad', 'country': 'India', 'doctype': 'State', 'name': 'Tamil Nad'}, 
		{'state_name': 'Tennessee', 'country': 'United States', 'doctype': 'State', 'name': 'Tennessee'}, 
		{'state_name': 'Texas', 'country': 'United States', 'doctype': 'State', 'name': 'Texas'}, 
		{'state_name': 'Tianjin', 'country': 'China', 'doctype': 'State', 'name': 'Tianjin'}, 
		{'state_name': 'Tripura', 'country': 'India', 'doctype': 'State', 'name': 'Tripura'}, 
		{'state_name': 'Turpan', 'country': 'China', 'doctype': 'State', 'name': 'Turpan'}, 
		{'state_name': 'Urumqi', 'country': 'China', 'doctype': 'State', 'name': 'Urumqi'}, 
		{'state_name': 'Utah', 'country': 'United States', 'doctype': 'State', 'name': 'Utah'}, 
		{'state_name': 'Uttar Pradesh', 'country': 'India', 'doctype': 'State', 'name': 'Uttar Pradesh'}, 
		{'state_name': 'Uttarakhand', 'country': 'India', 'doctype': 'State', 'name': 'Uttarakhand'}, 
		{'state_name': 'Vermont', 'country': 'United States', 'doctype': 'State', 'name': 'Vermont'}, 
		{'state_name': 'Virginia', 'country': 'United States', 'doctype': 'State', 'name': 'Virginia'}, 
		{'state_name': 'Washington', 'country': 'United States', 'doctype': 'State', 'name': 'Washington'}, 
		{'state_name': 'West Bengal', 'country': 'India', 'doctype': 'State', 'name': 'West Bengal'}, 
		{'state_name': 'West Virginia', 'country': 'United States', 'doctype': 'State', 'name': 'West Virginia'}, 
		{'state_name': 'Wisconsin', 'country': 'United States', 'doctype': 'State', 'name': 'Wisconsin'}, 
		{'state_name': 'Wuhan', 'country': 'China', 'doctype': 'State', 'name': 'Wuhan'}, 
		{'state_name': 'Wuxi', 'country': 'China', 'doctype': 'State', 'name': 'Wuxi'}, 
		{'state_name': 'Wyoming', 'country': 'United States', 'doctype': 'State', 'name': 'Wyoming'}, 
		{'state_name': 'Xiamen', 'country': 'China', 'doctype': 'State', 'name': 'Xiamen'}, 
		{'state_name': 'Xian', 'country': 'China', 'doctype': 'State', 'name': 'Xian'}, 
		{'state_name': 'Zhongshan ', 'country': 'China', 'doctype': 'State', 'name': 'Zhongshan'},
		
		# TDS Category
		{'category_name': '194J - Professional Fees - Non Company', 'doctype': 'TDS Category', 'name': '194J - Professional Fees - Non Company'}, 
		{'category_name': 'Commission Brokerage - for Companies', 'doctype': 'TDS Category', 'name': 'Commission Brokerage - for Companies'}, 
		{'category_name': 'Commission Brokerage - for Individuals', 'doctype': 'TDS Category', 'name': 'Commission Brokerage - for Individuals'}, 
		{'category_name': 'Contractors - 194C - for Companies', 'doctype': 'TDS Category', 'name': 'Contractors - 194C - for Companies'}, 
		{'category_name': 'Contractors - 194C - for Individuals', 'doctype': 'TDS Category', 'name': 'Contractors - 194C - for Individuals'}, 
		{'category_name': 'Pay to Advt Or Sub Contr - for Companies', 'doctype': 'TDS Category', 'name': 'Pay to Advt Or Sub Contr - for Companies'}, 
		{'category_name': 'Pay to Advt Or Sub Contr - for Individuals', 'doctype': 'TDS Category', 'name': 'Pay to Advt Or Sub Contr - for Individuals'}, 
		{'category_name': 'Professional Fees - 194J - for Companies', 'doctype': 'TDS Category', 'name': 'Professional Fees - 194J - for Companies'}, 
		{'category_name': 'Professional Fees - 194J - for Individuals', 'doctype': 'TDS Category', 'name': 'Professional Fees - 194J - for Individuals'}, 
		{'category_name': 'T.D.S on Other Interest - for Individuals', 'doctype': 'TDS Category', 'name': 'T.D.S on Other Interest - for Individuals'}, 
		{'category_name': 'T.D.S on Rent - for Companies', 'doctype': 'TDS Category', 'name': 'T.D.S on Rent - for Companies'}, 
		{'category_name': 'T.D.S on Rent - for Individuals', 'doctype': 'TDS Category', 'name': 'T.D.S on Rent - for Individuals'}, 
		{'category_name': 'TDS on ECB Loan', 'doctype': 'TDS Category', 'name': 'TDS on ECB Loan'}, 
		{'category_name': 'TDS on Rent (Machinery)', 'doctype': 'TDS Category', 'name': 'TDS on Rent (Machinery)'},
		
		# TDS Rate Chart
		{'applicable_from': '2010-07-01', 'name': 'Rate chart (01-07-2010)', 'module': 'Accounts', 'doctype': 'TDS Rate Chart'}, 
		{'category': 'Professional Fees - 194J - for Companies', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '1', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '10.0', 'slab_from': '30000.0', 'parentfield': 'rate_chart_detail'}, 
		{'category': 'Professional Fees - 194J - for Individuals', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '2', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '10.0', 'slab_from': '30000.0', 'parentfield': 'rate_chart_detail'}, 
		{'category': 'Contractors - 194C - for Companies', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '3', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '2.0', 'slab_from': '30000.0', 'parentfield': 'rate_chart_detail'}, 
		{'category': 'Contractors - 194C - for Individuals', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '4', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '1.0', 'slab_from': '30000.0', 'parentfield': 'rate_chart_detail'}, 
		{'category': 'T.D.S on Other Interest - for Individuals', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '5', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '10.0', 'slab_from': '5000.0', 'parentfield': 'rate_chart_detail'}, 
		{'category': 'Pay to Advt Or Sub Contr - for Companies', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '6', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '2.0', 'slab_from': '30000.0', 'parentfield': 'rate_chart_detail'}, 
		{'category': 'Pay to Advt Or Sub Contr - for Individuals', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '7', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '1.0', 'slab_from': '30000.0', 'parentfield': 'rate_chart_detail'}, 
		{'category': 'Commission Brokerage - for Companies', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '8', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '10.0', 'slab_from': '5000.0', 'parentfield': 'rate_chart_detail'}, 
		{'category': 'Commission Brokerage - for Individuals', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '9', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '10.0', 'slab_from': '5000.0', 'parentfield': 'rate_chart_detail'}, 
		{'category': 'T.D.S on Rent - for Companies', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '10', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '10.0', 'slab_from': '180000.0', 'parentfield': 'rate_chart_detail'}, 
		{'category': 'T.D.S on Rent - for Individuals', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '11', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '10.0', 'slab_from': '180000.0', 'parentfield': 'rate_chart_detail'}, 
		{'category': 'TDS on ECB Loan', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '12', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '10.0', 'slab_from': '5000.0', 'parentfield': 'rate_chart_detail'}, 
		{'category': 'TDS on Rent (Machinery)', 'parent': 'Rate chart (01-07-2010)', 'doctype': 'TDS Rate Detail', 'idx': '13', 'parenttype': 'TDS Rate Chart', 'rate_without_pan': '20.0', 'rate': '2.0', 'slab_from': '180000.0', 'parentfield': 'rate_chart_detail'},
		
		# GL Mapper - JV
		{'doc_type': 'Journal Voucher', 'name': 'Journal Voucher', 'doctype': 'GL Mapper'}, 
		{'voucher_type': 'parent:doctype', 'doctype': 'GL Mapper Detail', 'cost_center': 'cost_center', 'voucher_no': 'parent:name', 'against_voucher': "value:d.against_voucher or d.against_invoice or d.against_jv or ''", 'table_field': 'entries', 'transaction_date': 'parent:voucher_date', 'debit': 'debit', 'parent': 'Journal Voucher', 'company': 'parent:company', 'aging_date': 'parent:aging_date', 'fiscal_year': 'parent:fiscal_year', 'is_advance': 'is_advance', 'remarks': 'parent:remark', 'account': 'account', 'idx': '1', 'against_voucher_type': "value:(d.against_voucher and 'Purchase Invoice') or (d.against_invoice and 'Sales Invoice') or (d.against_jv and 'Journal Voucher') or ''", 'against': 'against_account', 'credit': 'credit', 'parenttype': 'GL Mapper', 'is_opening': 'parent:is_opening', 'posting_date': 'parent:posting_date', 'parentfield': 'fields'}, 
		{'voucher_type': 'doctype', 'doctype': 'GL Mapper Detail', 'voucher_no': 'name', 'transaction_date': 'voucher_date', 'debit': 'value:0', 'parent': 'Journal Voucher', 'company': 'company', 'aging_date': 'aging_date', 'fiscal_year': 'fiscal_year', 'remarks': 'remark', 'account': 'tax_code', 'idx': '2', 'against': 'supplier_account', 'credit': 'ded_amount', 'parenttype': 'GL Mapper', 'is_opening': 'is_opening', 'posting_date': 'posting_date', 'parentfield': 'fields'},
		# GL Mapper - POS
		{'doc_type': 'POS', 'name': 'POS', 'doctype': 'GL Mapper'}, 
		{'voucher_type': 'parent:doctype', 'doctype': 'GL Mapper Detail', 'cost_center': 'cost_center', 'voucher_no': 'parent:name',  'table_field': 'entries', 'transaction_date': 'parent:voucher_date', 'debit': 'value:0', 'parent': 'POS', 'company': 'parent:company', 'aging_date': 'parent:aging_date', 'fiscal_year': 'parent:fiscal_year', 'remarks': 'parent:remarks', 'account': 'income_account', 'idx': '1', 'against': 'parent:debit_to', 'credit': 'amount', 'parenttype': 'GL Mapper', 'is_opening': 'parent:is_opening', 'posting_date': 'parent:posting_date', 'parentfield': 'fields'}, 
		{'voucher_type': 'parent:doctype', 'doctype': 'GL Mapper Detail', 'cost_center': 'cost_center_other_charges', 'voucher_no': 'parent:name',  'table_field': 'other_charges', 'transaction_date': 'parent:voucher_date', 'debit': 'value:0', 'parent': 'POS', 'company': 'parent:company', 'aging_date': 'parent:aging_date', 'fiscal_year': 'parent:fiscal_year', 'remarks': 'parent:remarks', 'account': 'account_head', 'idx': '2', 'against': 'parent:debit_to', 'credit': 'tax_amount', 'parenttype': 'GL Mapper', 'is_opening': 'parent:is_opening', 'posting_date': 'parent:posting_date', 'parentfield': 'fields'}, 
		{'voucher_type': 'doctype', 'doctype': 'GL Mapper Detail', 'voucher_no': 'name', 'against_voucher': 'name',  'transaction_date': 'voucher_date', 'debit': 'grand_total', 'parent': 'POS', 'company': 'company', 'aging_date': 'aging_date', 'fiscal_year': 'fiscal_year', 'remarks': 'remarks', 'account': 'debit_to', 'idx': '3', 'against_voucher_type': 'doctype', 'against': 'against_income_account', 'credit': 'value:0', 'parenttype': 'GL Mapper', 'is_opening': 'is_opening', 'posting_date': 'posting_date', 'parentfield': 'fields'}, 
		{'voucher_type': 'doctype', 'doctype': 'GL Mapper Detail', 'voucher_no': 'name', 'against_voucher': 'name',  'transaction_date': 'voucher_date', 'debit': 'value:0', 'parent': 'POS', 'company': 'company', 'aging_date': 'aging_date', 'fiscal_year': 'fiscal_year', 'remarks': 'remarks', 'account': 'debit_to', 'idx': '4', 'against_voucher_type': 'doctype', 'against': 'cash_bank_account', 'credit': 'paid_amount', 'parenttype': 'GL Mapper', 'is_opening': 'is_opening', 'posting_date': 'posting_date', 'parentfield': 'fields'}, 
		{'voucher_type': 'doctype', 'doctype': 'GL Mapper Detail', 'voucher_no': 'name',  'transaction_date': 'voucher_date', 'debit': 'paid_amount', 'parent': 'POS', 'company': 'company', 'aging_date': 'aging_date', 'fiscal_year': 'fiscal_year', 'remarks': 'remarks', 'account': 'cash_bank_account', 'idx': '5', 'against': 'debit_to', 'credit': 'value:0', 'parenttype': 'GL Mapper', 'is_opening': 'is_opening', 'posting_date': 'posting_date', 'parentfield': 'fields'},
		# GL Mapper - POS with write off
		{'doc_type': 'POS with write off', 'doctype': 'GL Mapper', 'name': 'POS with write off'},
		{'account': 'income_account', 'against': 'parent:debit_to',  'aging_date': 'parent:aging_date', 'company': 'parent:company', 'cost_center': 'cost_center', 'credit': 'amount', 'debit': 'value:0', 'doctype': 'GL Mapper Detail', 'fiscal_year': 'parent:fiscal_year', 'idx': '1', 'is_opening': 'parent:is_opening', 'parent': 'POS with write off', 'parentfield': 'fields', 'parenttype': 'GL Mapper', 'posting_date': 'parent:posting_date', 'remarks': 'parent:remarks', 'table_field': 'entries', 'transaction_date': 'parent:voucher_date', 'voucher_no': 'parent:name', 'voucher_type': 'parent:doctype'},
		{'account': 'account_head', 'against': 'parent:debit_to',  'aging_date': 'parent:aging_date', 'company': 'parent:company', 'cost_center': 'cost_center_other_charges', 'credit': 'tax_amount', 'debit': 'value:0', 'doctype': 'GL Mapper Detail', 'fiscal_year': 'parent:fiscal_year', 'idx': '2', 'is_opening': 'parent:is_opening', 'parent': 'POS with write off', 'parentfield': 'fields', 'parenttype': 'GL Mapper', 'posting_date': 'parent:posting_date', 'remarks': 'parent:remarks', 'table_field': 'other_charges', 'transaction_date': 'parent:voucher_date', 'voucher_no': 'parent:name', 'voucher_type': 'parent:doctype'},
		{'account': 'debit_to', 'against': 'against_income_account', 'against_voucher': 'name', 'against_voucher_type': 'doctype', 'aging_date': 'aging_date', 'company': 'company', 'credit': 'value:0', 'debit': 'grand_total', 'doctype': 'GL Mapper Detail', 'fiscal_year': 'fiscal_year', 'idx': '3', 'is_opening': 'is_opening', 'parent': 'POS with write off', 'parentfield': 'fields', 'parenttype': 'GL Mapper', 'posting_date': 'posting_date', 'remarks': 'remarks',  'transaction_date': 'voucher_date', 'voucher_no': 'name', 'voucher_type': 'doctype'},
		{'account': 'debit_to', 'against': 'cash_bank_account', 'against_voucher': 'name', 'against_voucher_type': 'doctype', 'aging_date': 'aging_date', 'company': 'company', 'credit': 'paid_amount', 'debit': 'value:0', 'doctype': 'GL Mapper Detail', 'fiscal_year': 'fiscal_year', 'idx': '4', 'is_opening': 'is_opening', 'parent': 'POS with write off', 'parentfield': 'fields', 'parenttype': 'GL Mapper', 'posting_date': 'posting_date', 'remarks': 'remarks',  'transaction_date': 'voucher_date', 'voucher_no': 'name', 'voucher_type': 'doctype'},
		{'account': 'debit_to', 'against': 'write_off_account', 'against_voucher': 'name', 'against_voucher_type': 'doctype', 'aging_date': 'aging_date', 'company': 'company', 'credit': 'write_off_amount', 'debit': 'value:0', 'doctype': 'GL Mapper Detail', 'fiscal_year': 'fiscal_year', 'idx': '5', 'is_opening': 'is_opening', 'parent': 'POS with write off', 'parentfield': 'fields', 'parenttype': 'GL Mapper', 'posting_date': 'posting_date', 'remarks': 'remarks',  'transaction_date': 'voucher_date', 'voucher_no': 'name', 'voucher_type': 'doctype'},
		{'account': 'cash_bank_account', 'against': 'debit_to',  'aging_date': 'aging_date', 'company': 'company', 'credit': 'value:0', 'debit': 'paid_amount', 'doctype': 'GL Mapper Detail', 'fiscal_year': 'fiscal_year', 'idx': '6', 'is_opening': 'is_opening', 'parent': 'POS with write off', 'parentfield': 'fields', 'parenttype': 'GL Mapper', 'posting_date': 'posting_date', 'remarks': 'remarks',  'transaction_date': 'voucher_date', 'voucher_no': 'name', 'voucher_type': 'doctype'},
		{'account': 'write_off_account', 'against': 'debit_to', 'aging_date': 'aging_date', 'company': 'company', 'cost_center': 'write_off_cost_center', 'credit': 'value:0', 'debit': 'write_off_amount', 'doctype': 'GL Mapper Detail', 'fiscal_year': 'fiscal_year', 'idx': '7','is_opening': 'is_opening', 'parent': 'POS with write off', 'parentfield': 'fields', 'parenttype': 'GL Mapper', 'posting_date': 'posting_date', 'remarks': 'remarks',  'transaction_date': 'voucher_date', 'voucher_no': 'name', 'voucher_type': 'doctype'},
		# GL Mapper - Purchase Invoice
		{'doc_type': 'Purchase Invoice', 'name': 'Purchase Invoice', 'doctype': 'GL Mapper'}, 
		{'voucher_type': 'parent:doctype', 'doctype': 'GL Mapper Detail', 'cost_center': 'cost_center', 'voucher_no': 'parent:name',  'table_field': 'entries', 'transaction_date': 'parent:voucher_date', 'debit': 'amount', 'parent': 'Purchase Invoice', 'company': 'parent:company', 'aging_date': 'parent:aging_date', 'fiscal_year': 'parent:fiscal_year', 'remarks': 'parent:remarks', 'account': 'expense_head', 'idx': '1', 'against': 'parent:credit_to', 'credit': 'value:0', 'parenttype': 'GL Mapper', 'is_opening': 'parent:is_opening', 'posting_date': 'parent:posting_date', 'parentfield': 'fields'}, 
		{'voucher_type': 'parent:doctype', 'doctype': 'GL Mapper Detail', 'cost_center': 'cost_center', 'voucher_no': 'parent:name',  'table_field': 'purchase_tax_details', 'transaction_date': 'parent:voucher_date', 'debit': "value:d.fields.get('category') != 'For Valuation' and d.fields.get('add_deduct_tax') == 'Add' and d.fields.get('tax_amount') or 0", 'parent': 'Purchase Invoice', 'company': 'parent:company', 'aging_date': 'parent:aging_date', 'fiscal_year': 'parent:fiscal_year', 'remarks': 'parent:remarks', 'account': 'account_head', 'idx': '2', 'against': 'parent:credit_to', 'credit': "value:d.fields.get('category') != 'For Valuation' and d.fields.get('add_deduct_tax') == 'Deduct' and d.fields.get('tax_amount') or 0", 'parenttype': 'GL Mapper', 'is_opening': 'parent:is_opening', 'posting_date': 'parent:posting_date', 'parentfield': 'fields'}, 
		{'voucher_type': 'doctype', 'doctype': 'GL Mapper Detail', 'voucher_no': 'name',  'transaction_date': 'voucher_date', 'debit': 'value:0', 'parent': 'Purchase Invoice', 'company': 'company', 'aging_date': 'aging_date', 'fiscal_year': 'fiscal_year', 'remarks': 'remarks', 'account': 'tax_code', 'idx': '3', 'against': 'credit_to', 'credit': 'ded_amount', 'parenttype': 'GL Mapper', 'is_opening': 'is_opening', 'posting_date': 'posting_date', 'parentfield': 'fields'}, 
		{'voucher_type': 'doctype', 'doctype': 'GL Mapper Detail', 'voucher_no': 'name', 'against_voucher': 'name', 'transaction_date': 'voucher_date', 'debit': 'value:0', 'parent': 'Purchase Invoice', 'company': 'company', 'aging_date': 'aging_date', 'fiscal_year': 'fiscal_year', 'remarks': 'remarks', 'account': 'credit_to', 'idx': '4', 'against_voucher_type': "value:'Purchase Invoice'", 'against': 'against_expense_account', 'credit': 'total_amount_to_pay', 'parenttype': 'GL Mapper', 'is_opening': 'is_opening', 'posting_date': 'posting_date', 'parentfield': 'fields'},
		# GL Mapper - Purchase invoice with write off
		{'doc_type': 'Purchase Invoice with write off', 'doctype': 'GL Mapper', 'name': 'Purchase Invoice with write off'},
		{'account': 'expense_head', 'against': 'parent:credit_to', 'aging_date': 'parent:aging_date ', 'company': 'parent:company ', 'cost_center': 'cost_center ', 'credit': 'value:0 ', 'debit': 'amount ', 'doctype': 'GL Mapper Detail', 'fiscal_year': 'parent:fiscal_year ', 'is_opening': 'parent:is_opening ', 'posting_date': 'parent:posting_date ', 'remarks': 'parent:remarks ', 'table_field': 'entries ', 'transaction_date': 'parent:voucher_date ', 'voucher_no': 'parent:name ', 'voucher_type': 'parent:doctype ', 'doctype': 'GL Mapper Detail', 'parent': 'Purchase Invoice with write off ', 'parentfield': 'fields ', 'parenttype': 'GL Mapper'},
		{'account': 'account_head ', 'against': 'parent:credit_to ', 'aging_date': 'parent:aging_date ', 'company': 'parent:company ', 'cost_center': 'cost_center ', 'credit': "value:d.fields.get('category') != 'For Valuation' and d.fields.get('add_deduct_tax') == 'Deduct' and d.fields.get('tax_amount') or 0", 'debit': "value:d.fields.get('category') != 'For Valuation' and d.fields.get('add_deduct_tax') == 'Add' and d.fields.get('tax_amount') or 0",  'doctype': 'GL Mapper Detail', 'fiscal_year': 'parent:fiscal_year ', 'is_opening': 'parent:is_opening ', 'posting_date': 'parent:posting_date ', 'remarks': 'parent:remarks ', 'table_field': 'purchase_tax_details ', 'transaction_date': 'parent:voucher_date ', 'voucher_no': 'parent:name ', 'voucher_type': 'parent:doctype ', 'doctype': 'GL Mapper Detail', 'parent': 'Purchase Invoice with write off ', 'parentfield': 'fields ', 'parenttype': 'GL Mapper'},
		{'account': 'tax_code ', 'against': 'credit_to ', 'aging_date': 'aging_date ', 'company': 'company ', 'credit': 'ded_amount ', 'debit': 'value:0 ', 'doctype': 'GL Mapper Detail', 'fiscal_year': 'fiscal_year ', 'is_opening': 'is_opening ', 'posting_date': 'posting_date ', 'remarks': 'remarks ', 'transaction_date': 'voucher_date ', 'voucher_no': 'name ', 'voucher_type': 'doctype ', 'doctype': 'GL Mapper Detail', 'parent': 'Purchase Invoice with write off ', 'parentfield': 'fields ', 'parenttype': 'GL Mapper'},
		{'account': 'credit_to ', 'against': 'against_expense_account ', 'against_voucher': 'name ', 'against_voucher_type': "value:'Purchase Invoice'", 'aging_date': 'aging_date ', 'company': 'company ', 'credit': 'total_amount_to_pay ', 'debit': 'value:0 ', 'doctype': 'GL Mapper Detail', 'fiscal_year': 'fiscal_year ', 'is_opening': 'is_opening ', 'posting_date': 'posting_date ', 'remarks': 'remarks ', 'transaction_date': 'voucher_date ', 'voucher_no': 'name ', 'voucher_type': 'doctype', 'doctype': 'GL Mapper Detail', 'parent': 'Purchase Invoice with write off ', 'parentfield': 'fields ', 'parenttype': 'GL Mapper'},
		{'account': 'write_off_account ', 'against': 'credit_to ', 'aging_date': 'aging_date ', 'company': 'company ', 'cost_center': 'write_off_cost_center ', 'credit': 'write_off_amount ', 'debit': 'value:0 ', 'doctype': 'GL Mapper Detail', 'fiscal_year': 'fiscal_year ', 'is_opening': 'is_opening ', 'posting_date': 'posting_date ', 'remarks': 'remarks ', 'transaction_date': 'voucher_date ', 'voucher_no': 'name ', 'voucher_type': 'doctype', 'doctype': 'GL Mapper Detail', 'parent': 'Purchase Invoice with write off ', 'parentfield': 'fields ', 'parenttype': 'GL Mapper'},
		# GL Mapper - Sales Invoice
		{'doc_type': 'Sales Invoice', 'name': 'Sales Invoice', 'doctype': 'GL Mapper'}, 
		{'voucher_type': 'parent:doctype', 'doctype': 'GL Mapper Detail', 'cost_center': 'cost_center', 'voucher_no': 'parent:name',  'table_field': 'entries', 'transaction_date': 'parent:voucher_date', 'debit': 'value:0', 'parent': 'Sales Invoice', 'company': 'parent:company', 'aging_date': 'parent:aging_date', 'fiscal_year': 'parent:fiscal_year', 'remarks': 'parent:remarks', 'account': 'income_account', 'idx': '1', 'against': 'parent:debit_to', 'credit': 'amount', 'parenttype': 'GL Mapper', 'is_opening': 'parent:is_opening', 'posting_date': 'parent:posting_date', 'parentfield': 'fields'}, 
		{'voucher_type': 'parent:doctype', 'doctype': 'GL Mapper Detail', 'cost_center': 'cost_center_other_charges', 'voucher_no': 'parent:name',  'table_field': 'other_charges', 'transaction_date': 'parent:voucher_date', 'debit': 'value:0', 'parent': 'Sales Invoice', 'company': 'parent:company', 'aging_date': 'parent:aging_date', 'fiscal_year': 'parent:fiscal_year', 'remarks': 'parent:remarks', 'account': 'account_head', 'idx': '2', 'against': 'parent:debit_to', 'credit': 'tax_amount', 'parenttype': 'GL Mapper', 'is_opening': 'parent:is_opening', 'posting_date': 'parent:posting_date', 'parentfield': 'fields'}, 
		{'voucher_type': 'doctype', 'doctype': 'GL Mapper Detail', 'voucher_no': 'name', 'against_voucher': 'name', 'transaction_date': 'voucher_date', 'debit': 'grand_total', 'parent': 'Sales Invoice', 'company': 'company', 'aging_date': 'aging_date', 'fiscal_year': 'fiscal_year', 'remarks': 'remarks', 'account': 'debit_to', 'idx': '3', 'against_voucher_type': "value:'Sales Invoice'", 'against': 'against_income_account', 'credit': 'value:0', 'parenttype': 'GL Mapper', 'is_opening': 'is_opening', 'posting_date': 'posting_date', 'parentfield': 'fields'},

	]
	webnotes.conn.begin()
	create_doc(records, validate=1, on_update=1)
	webnotes.conn.commit()