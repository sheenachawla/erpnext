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

wn.require('public/app/js/buying.js');
// wn.require('app/utilities/doctype/sms_control/sms_control.js');

wn.provide("erpnext.buying");

erpnext.buying.PurchaseRequest = erpnext.Buying.extend({
	onload_post_render: function() {
		this.get_item_defaults();
	},
	
	refresh: function() {
		this._super();
		this.add_buttons();
	},

	posting_date: function() {
		if(this.frm.doc.__islocal && this.frm.doc.posting_date) {
			// on change of posting date, update schedule date
			this.set_schedule_date("purchase_request_items");
		}
	},
	
	qty: function(doc, cdt, cdn) {
		// warn if qty < min order qty
		var child = locals[cdt][cdn];
		if(flt(child.qty) < flt(child.min_order_qty)) {
			msgprint(repl("Warning: \
				Requested Quantity is less than Minimum Order Quantity \
				for Item: %(item_code)s at row # %(idx)s", 
				{ item_code: child.item_code, idx: child.idx }));
		}
	},
	
	get_item_defaults: function() {
		if(this.frm.doc.__islocal && wn.model.has_children(this.frm.doc.doctype,
				this.frm.doc.name, "purchase_request_items")) {
			$c_obj(wn.model.get_doclist(this.frm.doc.doctype, this.frm.doc.name),
				"set_item_defaults", null, function(r) {
					refresh_field("purchase_request_items");
				});
		}
	},
	
	add_buttons: function() {
		var me = this;
		this.frm.clear_custom_buttons();
		
		if(this.frm.doc.docstatus == 1) {
			if(this.frm.doc.is_stopped == 1) {
				this.frm.add_custom_button("Resume Purchase Request",
					function() { me.resume_purchase_request(this); }, "icon-play");
			} else {
				this.frm.add_custom_button("Make Supplier Quotation",
					function() { me.make_supplier_quotation(this); });
				
				if(this.frm.doc.per_ordered < 100.0) {
					this.frm.add_custom_button("Make Purchase Order",
						function() { me.make_purchase_order(this); });

					this.frm.add_custom_button("Stop Purchase Request",
						function() { me.stop_purchase_request(this); }, "icon-ban-circle");
				}
				this.frm.add_custom_button("Send SMS", this.send_sms);
			}
		}
	},
	
	make_supplier_quotation: function(btn) {
		wn.model.map_doclist([["Purchase Request", "Supplier Quotation"],
			["Purchase Request Item", "Supplier Quotation Item"]], this.frm.doc.name);
	},
	
	make_purchase_order: function(btn) {
		wn.model.map_doclist([["Purchase Request", "Purchase Order"],
			["Purchase Request Item", "Purchase Order Item"]], this.frm.doc.name);
	},
	
	stop_purchase_request: function(btn) {
		this.frm.doc.is_stopped = 1;
		this.frm.save(null, btn);
	},
	
	resume_purchase_request: function(btn) {
		this.frm.doc.is_stopped = 0;
		this.frm.save(null, btn);
	},
	
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

cur_frm.cscript = new erpnext.buying.PurchaseRequest({
	frm: cur_frm, item_table_field: "purchase_request_items"});