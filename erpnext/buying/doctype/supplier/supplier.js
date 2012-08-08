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

cur_frm.cscript.onload = function(doc,dt,dn){
	// history doctypes and scripts
	cur_frm.history_dict = {
		'Purchase Order' : 'cur_frm.cscript.make_po_list(this.body, this.doc)',
		'Purchase Receipt' : 'cur_frm.cscript.make_pr_list(this.body, this.doc)',
		'Purchase Invoice' : 'cur_frm.cscript.make_pi_list(this.body, this.doc)'
	}	
	// make communication, history list body
	cur_frm.cscript.make_hl_body();
	cur_frm.cscript.make_communication_body();
}

cur_frm.cscript.refresh = function(doc,dt,dn) {
	cur_frm.toggle_display('naming_series', (sys_defaults.supp_master_name != 'Supplier Name'));
	cur_frm.toggle_display(['address_html','contact_html'], !doc.__islocal);
    
	if(!doc.__islocal){
		// make lists
		cur_frm.cscript.make_address(doc,dt,dn);
		cur_frm.cscript.make_contact(doc,dt,dn);
		cur_frm.cscript.render_communication_list(doc, dt, dn);
		cur_frm.cscript.make_history(doc,dt,dn);
  }
}

// Transaction History
cur_frm.cscript.make_po_list = function(parent, doc) {
	flds = [
		"`tabPurchase Order`.status",
		"`tabPurchase Order`.currency",
		"ifnull(`tabPurchase Order`.grand_total_import, 0) as grand_total_import",		
	]
	cols_data = [
		{width: '3%', content: 'docstatus'},
		{width: '20%', content: 'name'},
		{width: '30%', content: 'status',
			css: {'text-align': 'right', 'color': '#777'}},
		{width: '35%', content: 'grand_total_import', css: {'text-align': 'right'}},
		{width: '12%', content:'modified', css: {'text-align': 'right'}}
	]
	cur_frm.cscript.get_common_list_view(parent, doc, 'Purchase Order', flds, cols_data);
}

cur_frm.cscript.make_pr_list = function(parent, doc) {
	flds = [
		"`tabPurchase Receipt`.status",
		"`tabPurchase Receipt`.currency",
		"ifnull(`tabPurchase Receipt`.grand_total_import, 0) as grand_total_import",
		"ifnull(`tabPurchase Receipt`.per_billed, 0) as per_billed",
	]
	cols_data = [
		{width: '3%', content: 'docstatus'},
		{width: '20%', content: 'name'},
		{width: '20%', content: 'status',
			css: {'text-align': 'right', 'color': '#777'}},
		{width: '35%', content: 'grand_total_import', css: {'text-align': 'right'}},
		{width: '10%', content: 'per_billed', type: 'bar-graph', label: 'Billed'},
		{width: '12%', content:'modified', css: {'text-align': 'right'}}
	]
	
	cur_frm.cscript.get_common_list_view(parent, doc, 'Purchase Receipt', flds, cols_data);
}

cur_frm.cscript.make_pi_list = function(parent, doc) {
	flds = [
		"`tabPurchase Invoice`.currency", 
		"ifnull(`tabPurchase Invoice`.grand_total_import, 0) as grand_total_import"
	]
	cols_data = [
		{width: '3%', content: 'docstatus'},
		{width: '30%', content: 'name'},
		{width: '55%', content: 'grand_total_import', css: {'text-align': 'right'}},
		{width: '12%', content:'modified', css: {'text-align': 'right'}}
	]
	cur_frm.cscript.get_common_list_view(parent, doc, 'Purchase Invoice', flds, cols_data);
}

cur_frm.cscript.get_common_list_view = function(parent, doc, dt, flds, cols_data) {
	var ListView = wn.views.ListView.extend({
		init: function(doclistview) {
			this._super(doclistview);
			this.fields = this.fields.concat(flds);
		},

		prepare_data: function(data) {
			this._super(data);
			data.grand_total_import = data.currency + " " + fmt_money(data.grand_total_import);
		},
		
		columns: cols_data,
	});
	
	cur_frm.cscript.render_list(doc, dt, parent, ListView);
}