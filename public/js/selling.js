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

erpnext.Selling = erpnext.Transaction.extend({
	onload_post_render: function() {
		var me = this;
		
		callback: function() {
			this.update_item_details();
		}
		this.hide_price_list_currency(callback);
	},
	hide_price_list_currency: function() {
		//to-do
	},
	update_item_details: function() {
		//to-do
	},
	set_missing_values: function() {
		if(this.frm.doc.price_list_name) 
			this.frm.doc.price_list_name = sys_defaults.price_list_name;
		if(this.frm.doc.price_list_currency) {
			this.frm.doc.price_list_currency = sys_defaults.price_list_currency;
			this.frm.doc.plc_exchange_rate = 1;
		}
	},
	customer_address: function() {
		if(this.frm.doc.customer) {
			get_server_fields('get_customer_address', JSON.stringify({
				customer: this.frm.doc.customer, 
				address: this.frm.doc.customer_address, 
				contact: this.frm.doc.contact_person
			}), '', this.frm.doc, this.frm.doc.doctype, this.frm.doc.name, 1);
	},
	contact_person: function() {
		this.customer_address();
	},
	customer_address.on_new: function(docname) {
		this.on_new_master("Address", docname);
	},
	contact_person.on_new: function(docname) {
		this.on_new_master("Contact", docname);
	},
	on_new_master: function(doctype, docname) {
		locals[doctype][docname].customer = 
		 	locals[this.frm.doc.doctype][this.frm.doc.name].customer;
		locals[doctype][docname].customer_name = 
		 	locals[this.frm.doc.doctype][this.frm.doc.name].customer_name;
	},
	price_list_name: function() {
		var me = this;
		var callback = function() {
			if(me.frm.doc.price_list_name && me.frm.doc.currency && me.frm.doc.price_list_currency
				 	&& me.frm.doc.exchange_rate && me.frm.doc.plc_exchange_rate) {
				wn.call({
					method: "runserverobj",
					"args": {
						docs: wn.model.compress(wn.model.get_doclist(me.frm.doc.doctype,
							me.frm.doc.name)),
						method: "get_price_list_rate",
					},
					callback: function(r, rt) {
						refresh_field(me.item_table_field);
						// to-do
						// recalculate amount and taxes
						
					}
				});
			}
		}
		this.hide_price_list_currency(callback);
	},
	setup_get_query: function() {
		this._super();
		var me = this;
		
		// item code
		this.frm.fields_dict[this.item_table_field].grid.get_field("item_code")
				.get_query = function() {
			if(inList(['Maintenance', 'Service'], me.frm.doc.order_type)) {
				var query = 'SELECT tabItem.name,tabItem.item_name,tabItem.description \
					FROM tabItem WHERE tabItem.is_service_item="Yes" \
					AND tabItem.docstatus != 2 \
					AND (ifnull(`tabItem`.`end_of_life`,"") = "" \
						OR `tabItem`.`end_of_life` > NOW() \
						OR `tabItem`.`end_of_life`="0000-00-00") \
					AND tabItem.%(key)s LIKE "%s" LIMIT 50';
			} else {
				var query = 'SELECT tabItem.name,tabItem.item_name,tabItem.description \
					FROM tabItem WHERE tabItem.is_sales_item="Yes" \
					AND tabItem.docstatus != 2 \
					AND (ifnull(`tabItem`.`end_of_life`,"") = "" \
						OR `tabItem`.`end_of_life` > NOW() \
						OR `tabItem`.`end_of_life`="0000-00-00") \
					AND tabItem.%(key)s LIKE "%s" LIMIT 50';
			}
			return query;
		}
		
		// customer address
		this.frm.fields_dict['customer_address'].get_query = function() {
			return "SELECT name, address_line1, city FROM tabAddress \
				WHERE customer = '" + me.frm.doc.customer + "' AND docstatus < 2 \
				AND name LIKE \"%s\" ORDER BY name ASC LIMIT 50";
		}

		// contact person
		this.frm.fields_dict['contact_person'].get_query = function() {
			return "SELECT name, CONCAT(first_name, ' ', ifnull(last_name, '')) AS FullName, \
			 	department, designation FROM tabContact \
				WHERE customer = '" + doc.customer +"' AND docstatus < 2 \
				AND name LIKE \"%s\" ORDER BY name ASC LIMIT 50";
		}
	},
})