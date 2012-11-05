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
			if(!me.frm.doc[key] && wn.meta.get_docfield(me.frm.doc.doctype, key)) {
				me.frm.doc[key] = value;
			}
		});
	},
	
	is_table_empty: function(table_field) {
		if(!wn.model.has_children(this.frm.doc.doctype, this.frm.doc.name, table_field)) {
			var error_msg = _("There should be atleast 1 Item in the Item table");
			msgprint(error_msg);
			throw error_msg;
		}
	},
	
	setup_get_query: function() {
		var me = this;
		
		// taxes and charges master
		if(this.frm.fields_dict.taxes_and_charges_master) {
			this.frm.fields_dict.taxes_and_charges_master.get_query = function() {
				return repl("select distinct name from `tab%(doctype)s` \
					where company = \"%(company)s\" and docstatus < 2 \
					and %(key)s like \"%s\" order by name limit 50", {
						doctype: wn.meta.get_docfield(me.frm.doc.doctype,
							"taxes_and_charges_master").options.split("\n")[0],
						company: me.frm.doc.company
					});
			}
		}
	},
	
	get_address: function(args) {
		wn.call({
			doc: this.frm.doc,
			method: 'get_address',
			args: args || {},
			callback: function(r) {
				me.frm.refresh();
			}
		});
	},
	
	get_contact: function(args) {
		wn.call({
			doc: this.frm.doc,
			method: 'get_contact',
			args: args || {},
			callback: function(r) {
				me.frm.refresh();
			}
		});
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
