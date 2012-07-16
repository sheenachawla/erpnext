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

"""
	All master data in one place

"""

masters = [
	# Customer Group
	{'doctype':'Customer Group', 'customer_group_name' : 'test_cust_group', 'name': 'test_cust_group', 'is_group': 'No', 'parent_customer_group':'All Customer Groups'}, 

	# item group
	{'doctype': 'Item Group', 'item_group_name': 'test_item_group', 'parent_item_group' : 'All Item Groups', 'is_group': 'No', 'name': 'test_item_group'},

	# territory
	{'doctype': 'Territory', 'territory_name': 'test_terr', 'is_group': 'No', 'name': 'test_terr', 'parent_territory': 'All Territories'},
		
	# supplier type
	{'doctype': 'Supplier Type', 'name': 'test_st', 'supplier_type': 'test_st'},
			
	# Sales Person
	{'doctype': 'Sales Person', 'name': 'test_sales_person', 'sales_person_name': 'test_sales_person'},

	# Customer
	{'doctype':'Customer', 'docstatus':0, 'customer_name' : 'test_customer', 'company' : 'Test Company', 'customer_group' : 'Default Customer Group', 'name': 'test_customer', 'credit_days': 30, 'credit_limit': 100000},

	# Supplier
	{'doctype': 'Supplier', 'supplier_name': 'test_supplier', 'name': 'test_supplier', 'supplier_type' : 'Default Supplier Type', 'company' : 'Test Company'},

	# Bank Account
	{'doctype':'Account', 'docstatus':0, 'account_name' : 'bank_acc', 'parent_account': 'Bank Accounts - TC', 'debit_or_credit': 'Debit', 'company' : 'Test Company', 'group_or_ledger' : 'Ledger', 'is_pl_account': 'No', 'name' : 'bank_acc - TC'},

	# Income Account
	{'doctype':'Account', 'docstatus':0, 'account_name' : 'income_acc', 'debit_or_credit': 'Credit', 'company' : 'Test Company', 'group_or_ledger' : 'Ledger', 'is_pl_account': 'Yes', 'name' : 'income_acc - TC', 'parent_account': 'Direct Income - TC'},
	
	# Expense Account
	{'doctype':'Account', 'docstatus':0, 'account_name' : 'expense_acc', 'debit_or_credit': 'Debit', 'company' : 'Test Company', 'group_or_ledger' : 'Ledger', 'is_pl_account': 'Yes', 'name' : 'expense_acc - TC', 'parent_account': 'Direct Expenses - TC'},

	# Tax Account
	{'doctype':'Account', 'docstatus':0, 'account_name' : 'tax_acc', 'debit_or_credit': 'Credit', 'company' : 'Test Company', 'group_or_ledger' : 'Ledger', 'is_pl_account': 'No', 'name' : 'tax_acc - TC', 'parent_account': 'Duties and Taxes - TC'},

	# Cost Center
	{'doctype':'Cost Center', 'docstatus':0, 'cost_center_name' : 'cc', 'parent_cost_center': 'Root - TC', 'group_or_ledger' : 'Ledger', 'name' : 'cc', 'company_name' : 'Test Company', 'company_abbr': 'TC'},
	
	#customer contact
	{'doctype': 'Contact', 'customer': 'test_customer', 'first_name': 'test_contact1', 'email_id': 'nabin@erpnext.com', 'is_primary_contact': '1'},
	
	#supplier contact
	{'doctype': 'Contact', 'supplier': 'test_supplier', 'first_name': 'test_contact2', 'email_id': 'nabin@erpnext.com', 'is_primary_contact': '1'},

	#address
	# Item
	# Stock item / non-serialized
	{'doctype': 'Item', 'docstatus': 0, 'name': 'test_item', 'item_name': 'test_item', 'item_code': 'test_item', \
	'item_group': 'Default Item Group', 'is_stock_item': 'Yes', 'has_serial_no': 'No', 'stock_uom': 'Nos', \
	'is_sales_item': 'Yes', 'is_purchase_item': 'Yes', 'is_service_item': 'No', 'is_sub_contracted_item': 'No', \
	'is_pro_applicable': 'Yes', 'is_manufactured_item': 'Yes'},
	{'doctype': 'Item Price', 'parentfield': 'ref_rate_details', 'parenttype': 'Item', 'parent' : 'test_item', \
	'price_list_name': 'test_pric_list', 'ref_currency': 'INR', 'ref_rate': 100},
	{'doctype': 'Item Tax', 'parentfield': 'item_tax', 'parenttype': 'Item', 'parent' : 'test_item', \
	'tax_type' : 'tax_acc - TC', 'tax_rate': 10},
	
	# Stock item / serialized
	{'doctype': 'Item', 'docstatus': 0, 'name': 'test_item_serialized', 'item_name': 'test_item_serialized', 'item_code': 'test_item_serialized', \
	'item_group': 'Default Item Group', 'is_stock_item': 'Yes', 'has_serial_no': 'Yes', 'stock_uom': 'Nos', \
	'is_sales_item': 'Yes', 'is_purchase_item': 'Yes', 'is_service_item': 'No', 'is_sub_contracted_item': 'No', \
	'is_pro_applicable': 'Yes', 'is_manufactured_item': 'Yes'},

	# Warehouse
	{'doctype': 'Warehouse', 'warehouse_name': 'test_wh1', 'name': 'test_wh1', 'warehouse_type': 'Stores'},
	{'doctype': 'Warehouse', 'warehouse_name': 'test_wh2', 'name': 'test_wh2', 'warehouse_type': 'Stores'},	

]