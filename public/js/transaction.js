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
	is_table_empty: function(table_field) {
		if(!wn.model.has_children(this.frm.doc.doctype, this.frm.doc.name, table_field)) {
			var error_msg = "There should be atleast 1 Item in the Item table";			
			msgprint(error_msg);
			throw error_msg;
		}
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