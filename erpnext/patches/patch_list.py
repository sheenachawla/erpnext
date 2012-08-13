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

patch_dict = {
	'00_00': [
		'update_patch_log',
	],
	
	'12_03': [
		'stable_branch_shift_09_01_12',
		'print_hide_totals',
		'rename_doctype_indent',
		'production_cleanup',
		'jan_production_patches',
		'allocated_to_profile',
		'remove_get_tds_button',
		'customer_address_contact_patch',
		'doclabel_in_doclayer',
		'email_settings_reload',
		'serial_no_add_opt',
		'cancel_purchase_returned',
		'deploy_packing_slip',
		'map_conversion_rate',
		'account_type_patch',
		'subcon_default_val',
		'website.all',
		'remove_archive',
		'no_copy_patch',
		'reload_item',
		'fix_packing_slip',
		'apps.todo_item',
		'convert_tables_to_utf8',
		'pending_patches',
		'pos_setting_patch',
		'reload_doctype',
		'reload_po_pr_mapper',
		'delete_pur_of_service',
		'navupdate',
		'label_cleanup',
		'add_roles_to_admin',
		'dt_map_fix',
		'reload_table',
		'remove_series_defval',
		'update_stockreco_perm',
		'stock_entry_others_patch',
		'reload_quote',
		'update_purpose_se',
		'update_se_fld_options',
		'pos_invoice_fix',
		'reload_mapper',
		'mapper_fix',
		'so_rv_mapper_fix',
		'clean_property_setter',
		'sync_ref_db',
		'rename_dt',
		'cleanup_control_panel',
		'doctype_get_refactor',
		'delete_docformat',
		'usertags',
	],
	
	'12_04': [
		'reload_c_form',
		'after_sync_cleanup',
		'change_cacheitem_schema',
		'remove_default_from_rv_detail',
		'update_role_in_address',
		'update_permlevel_in_address',
		'update_appraisal_permission',
		'serial_no_fixes',
		'repost_stock_for_posting_time',
		'naming_series_patch',
		'delete_about_contact',
	],
	
	'12_05': [
		'cleanup_property_setter',		
		'rename_prev_doctype',
		'cleanup_notification_control',
		'renamedt_in_custom_search_criteria',
		'stock_reco_patch',
		'cms',
		'reload_reports',
		'page_role_series_fix',
		'reload_sales_invoice_pf',
		'std_pf_readonly',
		'reload_so_pending_items',
		'customize_form_cleanup',
		'cs_server_readonly',
		'clear_session_cache',
		'same_purchase_rate_patch',
		'create_report_manager_role',
		'reload_customer_address_contact',
		'remove_euro_currency',
		'remove_communication_log',
	],
	
	'12_06': [
		'fetch_organization_from_lead',
		'copy_uom_for_pur_inv_item',
		'barcode_in_feature_setup',	
		'reports_list_permission',
		'support_ticket_autoreply',	
		'series_unique_patch', 
		'set_recurring_type',
		'alter_tabsessions',
		'delete_old_parent_entries',
		'cache_item_table',
		'cms2'
	],
	
	'12_07': [
		'reload_pr_po_mapper',
		'address_contact_perms',
		'packing_list_cleanup_and_serial_no',
		'deprecate_import_data_control',
		'default_freeze_account',
		'update_purchase_tax',
		'auth_table',
		'remove_event_role_owner_match',
		'sync_trial_balance',
		'drop_rename_tool',
		'deprecate_bulk_rename',
		'unicode_conf',
		'sync_trial_balance',
		'blog_guest_permission',
		'bin_permission',
		'project_patch_repeat',
		'repost_stock_due_to_wrong_packing_list',
		'supplier_quotation',
	],
	
	'12_08' : [
		'report_supplier_quotations',
		'task_allocated_to_assigned',
		'change_profile_permission'
	],

}