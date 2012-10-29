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

wn.require("app/js/transaction.js")
wn.provide("erpnext");

erpnext.Buying = erpnext.Transaction.extend({
	set_schedule_date: function(table_field) {
		// if children, then set schedule date based on lead time days
		if(wn.model.has_children(this.frm.doc.doctype, this.frm.doc.name, table_field)) {
			$c_obj(wn.model.get_doclist(this.frm.doc.doctype, this.frm.doc.name),
				"set_schedule_date", { table_field: table_field }, function(r) {
					refresh_field(table_field);
				})
		}
	},
	setup_get_query: function() {
		var me = this;

		// item_code
		this.frm.fields_dict[this.item_table_field].grid.get_field("item_code")
			.get_query = function() {
				if(me.frm.doc.is_subcontracted == "Yes") {
					var condition = "ifnull(is_subcontracted_item, 'No')='Yes'"
				} else {
					var condition = "ifnull(is_purchase_item, 'No')='Yes'"
				}
				var query = "select name, description from `tabItem` \
					where " + condition + " \
					and (ifnull(end_of_life, '')='' or end_of_life='0000-00-00' \
					or end_of_life > now()) and docstatus!=2 \
					and %(key)s like \"%s\" limit 50";
				
				return query;
			};
		
		
	},	
});