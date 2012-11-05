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

wn.provide("erpnext");

erpnext.Transaction = Class.extend({
	init: function(opts) {
		$.extend(this, opts);
		this.setup_get_query && this.setup_get_query();
		this.load_precision_maps && this.load_precision_maps();
	},
	onload: function() {
		this.set_missing_values();
	},
	refresh: function() {
		erpnext.hide_naming_series();
		if(this.add_buttons) {
			this.frm.clear_custom_buttons();
			this.add_buttons();
		}
		this.toggle_fields && this.toggle_fields();
		this.set_labels && this.set_labels();
	},
	set_missing_values: function() {
		var me = this;
		var default_values = {
			posting_date: dateutil.obj_to_str(new Date()),
			status: "Draft",
			company: sys_defaults.company,
			fiscal_year: sys_defaults.fiscal_year,
			currency: sys_defaults.currency,
			exchange_rate: 1.0,
			
			// for buying
			is_subcontracted: "No",
			
			// for selling
		}
		$.each(default_values, function(key, value) {
			if(!me.frm.doc[key]) me.frm.doc[key] = value;
		});	
	},
	item_code: function(doc, cdt, cdn) {
		var me = this;
		var item = locals[cdt][cdn];
		if(item.item_code) {
			wn.call({
				method: "runserverobj",
				args: {
					docs: wn.model.compress(wn.model.get_doclist(me.frm.doc.doctype,
						me.frm.doc.name)),
					method: "get_item_details",
					args: {
						item_code: item.item_code,
						warehouse: item.warehouse,
						income_account: item.income_account,
						expense_account: item.expense_account,
						cost_center: item.cost_center
					},
				},
				callback: function(r) {
					// update item doc
					$.extend(locals[cdt][cdn], r.message);
					refresh_field(me.item_table_field);
				}
			});
		}
		if(this.custom_item_code){
			this.custom_item_code(doc, cdt, cdn);
		}
	},
	barcode: function(doc, cdt, cdn) {
		var me = this;
		var item = locals[cdt][cdn];
		get_server_fields("get_barcode_details", item.barcode, this.item_table_field, 
			doc, cdt, cdn, 1, function(r, rt) {
				this.item_code(doc, cdt, cdn);
			}
		);
	},
	setup_get_query: function() {
		var me = this;
		// taxes and charges master
		this.frm.fields_dict['taxes_and_charges_master'].get_query = function() {
			return "SELECT DISTINCT name FROM `tabSales Taxes and Charges Master` \
				WHERE ifnull(company, '') = '" + me.frm.doc.company + "' \
				AND docstatus < 2 AND %(key)s LIKE \"%s\" ORDER BY name LIMIT 50";
		}
	},
});

erpnext.InputDialog = function(title, input_label, method) {
	var me = this;
	dialog = new Dialog(400, 400, title);
	dialog.make_body([
		['Text', input_label],
		['HTML', 'response_area', '<div class = "comment" id="response"></div>'],
		['HTML', 'button_area', '<div></div>']
	]);
	var add_button = $a($i(dialog.widgets['button_area']), 'button', 'button');
	add_button.innerHTML = 'Add';
	add_button.onclick = function() { dialog.add(); }

	var cancel_button = $a($i(dialog.widgets['button_area']), 'button', 'button');
	cancel_button.innerHTML = 'Cancel';
	$y(cancel_button, { marginLeft: '4px' });
	cancel_button.onclick = function() { dialog.hide(); };
	
	dialog.onshow = function() {
		dialog.widgets[input_label].value = '';
		$i('response').innerHTML = '';
	}

	dialog.add = function() {
		$i('response').innerHTML = 'Processing...';
		var arg = strip(dialog.widgets[input_label].value);
		if(arg) {
			wn.call({
				method: "runserverobj",
				args: {
					docs: wn.model.compress(wn.model.get_doclist(me.frm.doc.doctype,
						me.frm.doc.name)),
					method: method,
					args: arg
				},
				callback: function(r, rt) {
					if(r.message) {
						$i('response').innerHTML = 'Done';
						dialog.hide();
					}
				}
			});
		} else {
			$i('response').innerHTML = 'Please enter somthing before adding';
		}
	}
}
