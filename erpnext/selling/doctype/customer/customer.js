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

wn.require('erpnext/setup/doctype/contact_control/contact_control.js');
wn.require('erpnext/support/doctype/communication/communication.js');
wn.require('erpnext/controllers/party.js');


/* ********************************* onload ********************************************* */

cur_frm.cscript.onload = function(doc,dt,dn){
	// history doctypes and scripts
	cur_frm.history_dict = {
		'Quotation' : 'cur_frm.cscript.make_qtn_list(this.body, this.doc)',
		'Sales Order' : 'cur_frm.cscript.make_so_list(this.body, this.doc)',
		'Delivery Note' : 'cur_frm.cscript.make_dn_list(this.body, this.doc)',
		'Sales Invoice' : 'cur_frm.cscript.make_si_list(this.body, this.doc)'
	}
	// make address, contact, shipping, history list body
	cur_frm.cscript.make_hl_body();
	cur_frm.cscript.load_defaults(doc, dt, dn);	
	cur_frm.cscript.make_communication_body();
}

cur_frm.cscript.load_defaults = function(doc, dt, dn) {
	doc = locals[doc.doctype][doc.name];
	if (doc.__islocal && doc.lead_name) {
		var fields_to_refresh = LocalDB.set_default_values(doc);
		if(fields_to_refresh) refresh_many(fields_to_refresh);
	}
}

cur_frm.cscript.refresh = function(doc,dt,dn) {
	cur_frm.toggle_display('naming_series', (sys_defaults.cust_master_name != 'Customer Name'))
	cur_frm.toggle_display(['address_html','contact_html'], !doc.__islocal);

	if(!doc.__islocal){
		cur_frm.cscript.make_address(doc,dt,dn);
		cur_frm.cscript.make_contact(doc,dt,dn);
		cur_frm.cscript.make_history(doc,dt,dn);
		cur_frm.cscript.render_communication_list(doc, cdt, cdn);
	}
}

cur_frm.add_fetch('lead_name', 'company_name', 'customer_name');
cur_frm.add_fetch('default_sales_partner','commission_rate','default_commission_rate');

// Transaction History
// functions called by these functions are defined in communication.js
cur_frm.cscript.make_qtn_list = function(parent, doc) {
	cur_frm.cscript.get_common_list_view(parent, doc, 'Quotation');
}

cur_frm.cscript.make_so_list = function(parent, doc) {
	cur_frm.cscript.get_common_list_view(parent, doc, 'Sales Order');
}

cur_frm.cscript.make_dn_list = function(parent, doc) {
	cur_frm.cscript.get_common_list_view(parent, doc, 'Delivery Note');
}

cur_frm.cscript.get_common_list_view = function(parent, doc, doctype) {
	var ListView = wn.views.ListView.extend({
		init: function(doclistview) {
			this._super(doclistview);
			this.fields = this.fields.concat([
				"`tab" + doctype + "`.status",
				"`tab" + doctype + "`.currency",
				"ifnull(`tab" + doctype + "`.grand_total_export, 0) as grand_total_export",
				
			]);
		},

		prepare_data: function(data) {
			this._super(data);
			data.grand_total_export = data.currency + " " + fmt_money(data.grand_total_export)
		},

		columns: [
			{width: '3%', content: 'docstatus'},
			{width: '25%', content: 'name'},
			{width: '25%', content: 'status'},
			{width: '35%', content: 'grand_total_export', css: {'text-align': 'right'}},			
			{width: '12%', content:'modified', css: {'text-align': 'right'}}		
		],
	});
	
	cur_frm.cscript.render_list(doc, doctype, parent, ListView);
}


cur_frm.cscript.make_si_list = function(parent, doc) {
	var ListView = wn.views.ListView.extend({
		init: function(doclistview) {
			this._super(doclistview);
			this.fields = this.fields.concat([
				"ifnull(`tabSales Invoice`.outstanding_amount, 0) as outstanding_amount",
				"`tabSales Invoice`.currency",
				"ifnull(`tabSales Invoice`.conversion_rate, 0) as conversion_rate",
				"ifnull(`tabSales Invoice`.grand_total_export, 0) as grand_total_export",
				
			]);
		},

		prepare_data: function(data) {
			this._super(data);
			if (data.outstanding_amount) {
				data.outstanding_amount = data.currency + " " + 
					fmt_money(flt(data.outstanding_amount)/flt(data.conversion_rate)) + 
					" [outstanding]";
				
			} else {
				data.outstanding_amount = '';
			}
			data.grand_total_export = data.currency + " " + fmt_money(data.grand_total_export);
		},

		columns: [
			{width: '3%', content: 'docstatus'},
			{width: '25%', content: 'name'},
			{width: '25%', content: 'outstanding_amount',
				css: {'text-align': 'right', 'color': '#777'}},
			{width: '35%', content: 'grand_total_export', css: {'text-align': 'right'}},
			{width: '12%', content:'modified', css: {'text-align': 'right'}}
		],
	});
	
	cur_frm.cscript.render_list(doc, 'Sales Invoice', parent, ListView);
}