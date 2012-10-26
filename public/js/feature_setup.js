// ERPNext - web based ERP (http://erpnext.com)
// Copyright (C) 2012 Web Notes Technologies Pvt Ltd
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

/* features setup "Dictionary", "Script"
Dictionary Format
	'projects': {
		'Sales Order': {
			'fields':['project_name'],
			'sales_order_items':['projected_qty']
		},
		'Purchase Order': {
			'fields':['project_name']
		}
	}
// ====================================================================*/
pscript.feature_dict = {
	'fs_projects': {
		'BOM': {'fields':['project_name']},
		'Delivery Note': {'fields':['project_name']},
		'Purchase Invoice': {'purchase_invoice_items':['project_name']},
		'Production Order': {'fields':['project_name']},
		'Purchase Order': {'purchase_order_items':['project_name']},
		'Purchase Receipt': {'purchase_receipt_details':['project_name']},
		'Sales Invoice': {'fields':['project_name']},
		'Sales Order': {'fields':['project_name']},
		'Stock Entry': {'fields':['project_name']},
		'Timesheet': {'timesheet_details':['project_name']}
	},
	'fs_delivery_note_packing_items': {
		//'Delivery Note': {'fields':['delivery_note_packing_items','print_packing_slip','packing_checked_by','packed_by','pack_size','shipping_mark'],'delivery_note_items':['no_of_packs','pack_gross_wt','pack_nett_wt','pack_no','pack_unit']},
		//'Sales Order': {'fields':['delivery_note_packing_items']}
	},
	'fs_discounts': {
		'Delivery Note': {'delivery_note_items':['discount']},
		'Quotation': {'quotation_items':['discount']},
		'Sales Invoice': {'sales_invoice_items':['discount']},
		'Sales Order': {'sales_order_items':['discount','ref_rate']}
	},
	'fs_purchase_discounts': {
		'Purchase Order': {'purchase_order_items':['ref_rate', 'discount', 'print_ref_rate']},
		'Purchase Receipt': {'purchase_receipt_details':['ref_rate', 'discount', 'print_ref_rate']},
		'Purchase Invoice': {'purchase_invoice_items':['ref_rate', 'discount', 'print_ref_rate']}
	},
	'fs_brands': {
		'Delivery Note': {'delivery_note_items':['brand']},
		'Purchase Request': {'purchase_request_items':['brand']},
		'Item': {'fields':['brand']},
		'Purchase Order': {'purchase_order_items':['brand']},
		'Purchase Invoice': {'purchase_invoice_items':['brand']},
		'Quotation': {'quotation_items':['brand']},
		'Sales Invoice': {'sales_invoice_items':['brand']},
		'Sales BOM': {'fields':['new_item_brand']},
		'Sales Order': {'sales_order_items':['brand']},
		'Serial No': {'fields':['brand']}
	},
	'fs_after_sales_installations': {
		'Delivery Note': {'fields':['installation_status','per_installed'],'delivery_note_items':['installed_qty']}
	},
	'fs_item_batch_nos': {
		'Delivery Note': {'delivery_note_items':['batch_no']},
		'Item': {'fields':['has_batch_no']},
		'Purchase Receipt': {'purchase_receipt_details':['batch_no']},
		'Quality Inspection': {'fields':['batch_no']},
		'Sales and Pruchase Return Wizard': {'return_details':['batch_no']},
		'Sales Invoice': {'sales_invoice_items':['batch_no']},
		'Stock Entry': {'mtn_details':['batch_no']},
		'Stock Ledger Entry': {'fields':['batch_no']}
	},
	'fs_item_serial_nos': {
		'Customer Issue': {'fields':['serial_no']},
		'Delivery Note': {'delivery_note_items':['serial_no'],'delivery_note_packing_items':['serial_no']},
		'Installation Note': {'installed_item_details':['serial_no']},
		'Item': {'fields':['has_serial_no']},
		'Maintenance Schedule': {'item_maintenance_detail':['serial_no'],'maintenance_schedule_detail':['serial_no']},
		'Maintenance Visit': {'maintenance_visit_details':['serial_no']},
		'Purchase Receipt': {'purchase_receipt_details':['serial_no']},
		'Quality Inspection': {'fields':['item_serial_no']},
		'Sales and Pruchase Return Wizard': {'return_details':['serial_no']},
		'Sales Invoice': {'sales_invoice_items':['serial_no']},
		'Stock Entry': {'mtn_details':['serial_no']},
		'Stock Ledger Entry': {'fields':['serial_no']}
	},
	'fs_item_barcode': {
		'Item': {'fields': ['barcode']},
		'Delivery Note': {'delivery_note_items': ['barcode']},
		'Sales Invoice': {'sales_invoice_items': ['barcode']}
	},
	'fs_item_group_in_details': {
		'Delivery Note': {'delivery_note_items':['item_group']},
		'Opportunity': {'opportunity_items':['item_group']},
		'Purchase Request': {'purchase_request_items':['item_group']},
		'Item': {'fields':['item_group']},
		'Global Defaults': {'fields':['default_item_group']},
		'Purchase Order': {'purchase_order_items':['item_group']},
		'Purchase Receipt': {'purchase_receipt_details':['item_group']},
		'Purchase Voucher': {'entries':['item_group']},
		'Quotation': {'quotation_items':['item_group']},
		'Sales Invoice': {'sales_invoice_items':['item_group']},
		'Sales BOM': {'fields':['serial_no']},
		'Sales Order': {'sales_order_items':['item_group']},
		'Serial No': {'fields':['item_group']},
		'Sales Partner': {'partner_target_details':['item_group']},
		'Sales Person': {'target_details':['item_group']},
		'Territory': {'target_details':['item_group']}
	},
	'fs_page_break': {
		'Delivery Note': {'delivery_note_items':['page_break'],'delivery_note_packing_items':['page_break']},
		'Purchase Request': {'purchase_request_items':['page_break']},
		'Purchase Order': {'purchase_order_items':['page_break']},
		'Purchase Receipt': {'purchase_receipt_details':['page_break']},
		'Purchase Voucher': {'entries':['page_break']},
		'Quotation': {'quotation_items':['page_break']},
		'Sales Invoice': {'sales_invoice_items':['page_break']},
		'Sales Order': {'sales_order_items':['page_break']}
	},
	'fs_exports': {
		'Delivery Note': {'fields':['Note','exchange_rate','currency','grand_total_print','rounded_total_in_words_print','rounded_total_print'],'delivery_note_items':['ref_rate','amount','rate']},
		'POS Setting': {'fields':['exchange_rate','currency']},
		'Quotation': {'fields':['Note HTML','OT Notes','exchange_rate','currency','grand_total_print','rounded_total_in_words_print','rounded_total_print'],'quotation_items':['ref_rate','amount','rate']},
		'Sales Invoice': {'fields':['exchange_rate','currency','grand_total_print','rounded_total_in_words_print','rounded_total_print'],'sales_invoice_items':['ref_rate','amount','rate']},
		'Item': {'ref_rate_details':['ref_currency']},
		'Sales BOM': {'fields':['currency']},
		'Sales Order': {'fields':['Note1','OT Notes','exchange_rate','currency','grand_total_print','rounded_total_in_words_print','rounded_total_print'],'sales_order_items':['ref_rate','amount','rate']}
	},
	'fs_imports': {
		'Purchase Invoice': {'fields':['exchange_rate','currency','grand_total_print','grand_total_in_words_print','net_total_print','other_charges_added_import','other_charges_deducted_import'],'purchase_invoice_items':['ref_rate', 'amount','rate']},
		'Purchase Order': {'fields':['Note HTML','exchange_rate','currency','grand_total_print','grand_total_in_words_print','net_total_print','other_charges_added_import','other_charges_deducted_import'],'purchase_order_items':['ref_rate', 'amount','rate']},
		'Purchase Receipt': {'fields':['exchange_rate','currency','grand_total_print','grand_total_in_words_print','net_total_print','other_charges_added_import','other_charges_deducted_import'],'purchase_receipt_details':['ref_rate','amount','rate']},
		'Supplier Quotation': {'fields':['exchange_rate','currency']}
	},
	'fs_item_advanced': {
		'Item': {'fields':['item_customer_details']}
	},
	'fs_sales_extras': {
		'Address': {'fields':['sales_partner']},
		'Contact': {'fields':['sales_partner']},
		'Customer': {'fields':['sales_team']},
		'Delivery Note': {'fields':['sales_team','Packing List']},
		'Item': {'fields':['item_customer_details']},
		'Sales Invoice': {'fields':['sales_team']},
		'Sales Order': {'fields':['sales_team','Packing List']}
	},
	'fs_more_info': {
		'Delivery Note': {'fields':['More Info']},
		'Opportunity': {'fields':['More Info']},
		'Purchase Request': {'fields':['More Info']},
		'Lead': {'fields':['More Info']},
		'Purchase Invoice': {'fields':['More Info']},
		'Purchase Order': {'fields':['More Info']},
		'Purchase Receipt': {'fields':['More Info']},
		'Quotation': {'fields':['More Info']},
		'Sales Invoice': {'fields':['More Info']},
		'Sales Order': {'fields':['More Info']},
	},
	'fs_quality': {
		'Item': {'fields':['Item Inspection Criteria','inspection_required']},
		'Purchase Receipt': {'purchase_receipt_details':['qa_no']}
	},
	'fs_manufacturing': {
		'Item': {'fields':['Manufacturing']}
	},
	'fs_pos': {
		'Sales Invoice': {'fields':['is_pos']}
	},
	'fs_recurring_invoice': {
		'Sales Invoice': {'fields': ['Recurring Invoice']}
	}
}

$(document).bind('form_refresh', function() {
	for(sys_feat in sys_defaults)
	{
		if(sys_defaults[sys_feat]=='0' && (sys_feat in pscript.feature_dict)) //"Features to hide" exists
		{
			if(cur_frm.doc.doctype in  pscript.feature_dict[sys_feat])
			{
				for(fort in pscript.feature_dict[sys_feat][cur_frm.doc.doctype])
				{
					if(fort=='fields')
						hide_field(pscript.feature_dict[sys_feat][cur_frm.doc.doctype][fort]);
					else if(cur_frm.fields_dict[fort])
					{
						for(grid_field in pscript.feature_dict[sys_feat][cur_frm.doc.doctype][fort])
							cur_frm.fields_dict[fort].grid.set_column_disp(pscript.feature_dict[sys_feat][cur_frm.doc.doctype][fort][grid_field], false);
					}
					else
						msgprint('Grid "'+fort+'" does not exists');
				}
			}
		}
	}
})
