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

wn.require("app/accounts/doctype/purchase_taxes_and_charges_master/purchase_taxes_and_charges_master.js");
wn.require("public/app/js/buying.js");
// wn.require('app/utilities/doctype/sms_control/sms_control.js');

wn.provide("erpnext.buying");

erpnext.buying.SupplierQuotation = erpnext.Buying.extend({
	// onload_post_render: function() {
	// 	this.get_item_defaults();
	// },
	refresh: function() {
		this._super();
	},
	toggle_fields: function() {
		this.frm.toggle_display("contact_section", this.frm.doc.supplier);
	},
	set_labels: function() {
		
	},
	
	// validate: function() {
	// 	this.is_table_empty("purchase_request_items");
	// },
	// posting_date: function() {
	// 	if(this.frm.doc.__islocal && this.frm.doc.posting_date) {
	// 		// on change of posting date, update schedule date
	// 		this.set_schedule_date("purchase_request_items");
	// 	}
	// },
	// qty: function(doc, cdt, cdn) {
	// 	// warn if qty < min order qty
	// 	var child = locals[cdt][cdn];
	// 	if(flt(child.qty) < flt(child.min_order_qty)) {
	// 		msgprint(repl("Warning: \
	// 			Requested Quantity is less than Minimum Order Quantity \
	// 			for Item: %(item_code)s at row # %(idx)s", 
	// 			{ item_code: child.item_code, idx: child.idx }));
	// 	}
	// },
	// get_item_defaults: function() {
	// 	if(this.frm.doc.__islocal && wn.model.has_children(this.frm.doc.doctype,
	// 			this.frm.doc.name, "purchase_request_items")) {
	// 		$c_obj(wn.model.get_doclist(this.frm.doc.doctype, this.frm.doc.name),
	// 			"set_item_defaults", null, function(r) {
	// 				refresh_field("purchase_request_items");
	// 			});
	// 	}
	// },
	add_buttons: function() {
		var me = this;
		
		if(this.frm.doc.docstatus == 1) {
			this.frm.add_custom_button("Make Purchase Order",
				function() { me.make_purchase_order(this); });
		}
	},
	make_purchase_order: function(btn) {
		wn.model.map_doclist([["Supplier Quotation", "Purchase Order",
			["Supplier Quotation Item", "Purchase Order Item"],
			["Purchase Taxes and Charges", "Purchase Taxes and Charges"]]],
			this.frm.doc.name)
	}
	send_sms: function(me) {
		// TODO
	},
	load_precision_maps: function() {
		// TODO
		// if(!this.frm.precision) this.frm.precision = {};
		// this.frm.precision.main = wn.model.get_precision_map("Purchase Request");
		// this.frm.precision.item = wn.model.get_precision_map("Purchase Request Item");
	}
})

cur_frm.cscript = new erpnext.buying.SupplierQuotation({
	frm: cur_frm, item_table_field: "supplier_quotation_items"});


// =======
// }
// 
// cur_frm.cscript.make_purchase_order = function() {
// 	var new_po_name = createLocal("Purchase Order");
// 	$c("dt_map", {
// 		"docs": compress_doclist([locals['Purchase Order'][new_po_name]]),
// 		"from_doctype": cur_frm.doc.doctype,
// 		"to_doctype": "Purchase Order",
// 		"from_docname": cur_frm.doc.name,
// 		"from_to_list": JSON.stringify([['Supplier Quotation', 'Purchase Order'],
// 			['Supplier Quotation Item', 'Purchase Order Item'],
// 			['Purchase Taxes and Charges', 'Purchase Taxes and Charges']]),
// 	}, function(r, rt) { loaddoc("Purchase Order", new_po_name) });
// }
// 
// cur_frm.cscript.supplier = function(doc, dt, dn) {
// 	if (doc.supplier) {
// 		get_server_fields('get_default_supplier_address',
// 			JSON.stringify({ supplier: doc.supplier }), '', doc, dt, dn, 1,
// 			function() { cur_frm.refresh(); });
// 		cur_frm.cscript.toggle_contact_section(doc);
// 	}
// }
// 
// cur_frm.cscript.uom = function(doc, cdt, cdn) {
// 	// no need to trigger updation of stock uom, as this field doesn't exist in supplier quotation
// }
// 
// cur_frm.fields_dict['quotation_items'].grid.get_field('project_name').get_query = 
// 	function(doc, cdt, cdn) {
// 		return "select `tabProject`.name from `tabProject` \
// 			where `tabProject`.status not in (\"Completed\", \"Cancelled\") \
// 			and `tabProject`.name like \"%s\" \
// 			order by `tabProject`.name ASC LIMIT 50";
// >>>>>>> 282a97f954fcde11cc97a028b19301beef324a94