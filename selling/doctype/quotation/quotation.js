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

wn.require('public/app/js/selling.js');
wn.provide("erpnext.selling");

erpnext.selling.Quotation = erpnext.Selling.extend({
	onload: function() {
		this._super();
		this.hide_unhide_fields();
		this.make_communication_body();
	},
	refresh: function() {
		this._super();
		this.add_button();
		this.hide_unhide_fields();
		
		if (!this.is_onload) this.hide_price_list_currency(); 
		if (!doc.__islocal) this.render_communication_list();
	},
	validate: function() {
		this.validate_quotation_to();
	},
	validate_quotation_to: function() {
		if(this.frm.doc.quotation_to == "Lead" && !this.frm.doc.lead) {
			msgprint("Lead is mandatory");
			validated = false;
		} else if (this.frm.doc.quotation_to == "Customer" && !this.frm.doc.customer) {
			msgprint("Customer is mandatory");
			validated = false;
		}
	},
	on_submit: function() {
		this.notify(this.frm.doc, {type: 'Quotation', doctype: 'Quotation'});
	},
	hide_unhide_fields: function() {
		erpnext.hide_naming_series();
		var quote_to_customer = ['customer','customer_address',
			'contact_person', 'customer_name', 'contact_display', 'customer_group'];
		var quote_to_lead = ['lead', 'lead_name', 'organization'];
		this.frm.toggle_display(quote_to_customer, this.frm.doc.quotation_to == "Customer");
		this.frm.toggle_display(quote_to_lead, this.frm.doc.quotation_to == "Lead");
		
		display_contact_section = (this.frm.doc.customer || this.frm.doc.lead) ? true : false;
		$(this.frm.fields_dict.contact_section.row.wrapper).toggle(display_contact_section);
	},
	

	cur_frm.cscript.lead_cust_show = function(doc,cdt,cdn){
		hide_field(['lead', 'lead_name','customer','customer_address','contact_person',
			'customer_name','address_display','contact_display','contact_mobile','contact_email',
			'territory','customer_group', 'organization']);
		if(doc.quotation_to == 'Lead') unhide_field(['lead']);
		else if(doc.quotation_to == 'Customer') unhide_field(['customer']);

		doc.lead = doc.lead_name = doc.customer = doc.customer_name = doc.customer_address = doc.contact_person = doc.address_display = doc.contact_display = doc.contact_mobile = doc.contact_email = doc.territory = doc.customer_group = doc.organization = "";
	}

	cur_frm.cscript.quotation_to = function(doc,cdt,cdn){
		cur_frm.cscript.lead_cust_show(doc,cdt,cdn);
	}
	add_button: function() {
		this.frm.clear_custom_buttons();		
		if(this.frm.doc.docstatus == 1 && this.frm.doc.status != 'Order Lost') {
			this.frm.add_custom_button('Make Sales Order', this.make_sales_order);
			this.frmcur_frm.add_custom_button('Set as Lost', this.set_as_lost);
			this.frmcur_frm.add_custom_button('Send SMS', this.send_sms); // to-do
		}
	},
	make_sales_order: function() {
		wn.model.map_doclist([["Quotation", "Sales Order"], 
			["Quotation Item", "Sales Order Item"],
		 	['Sales Taxes and Charges','Sales Taxes and Charges'], 
			['Sales Team', 'Sales Team']], this.frm.doc.name);
	},
	set_as_lost: function() {
		// to-do (discuss with anand)
	},
	lead: function() {
		if(this.frm.doc.lead) {
			get_server_fields('get_lead_details', this.frm.doc.lead, '', this.frm.doc, 
				this.frm.doc.doctype, this.frm.doc.name, 1);
			unhide_field('territory');
		}
	},
	setup_get_query: function() {
		this._super();
		var me = this;
		
		//lead
		this.frm.fields_dict['lead'].get_query = function() {
			return "SELECT name, lead_name FROM tabLead \
				WHERE %(key)s LIKE \"%s\" ORDER BY name ASC LIMIT 50";
		}
		
		// opportunity
		this.frm.fields_dict['opportunity'].get_query = function() {
			var condition = "";
			if(me.frm.doc.order_type) {
				condition += " AND ifnull(enquiry_type, '') = '" + me.frm.doc.order_type + "'";
			}
			if(me.frm.doc.customer) {
				condition += " AND customer = '" + me.frm.doc.customer + "'";
			} else if(me.frm.doc.lead) {
				condition += " AND lead = '" + me.frm.doc.lead + "'";
			}
			
			return "SELECT name FROM tabOpportunity WHERE docstatus = 1 \
				AND status = 'Submitted' AND %(key)s like \"%s\"" + condition + 
				"ORDER BY name ASC LIMIT 50";
		}
		
		// item code
		this.frm.fields_dict[this.item_table_field].grid.get_field('item_code')
				.get_query = function() {
			if(me.frm.doc.order_type == "Maintenance") {
				var condition = "infull(item.is_service_item, 'No')='Yes'";
			} else {
				var condition = "ifnull(item.is_sales_item, 'No')='Yes'";
			}
			
			if(me.frm.doc.customer) {
				var print_rate_field = wn.meta.get_docfield(me.frm.doctype, 
					'print_rate', me.frm.doc.name);
				var precision = (print_rate_field && 
					print_rate_field.fieldtype === 'Float') ? 6 : 2;
				var query = repl("\
					select \
						item.name, \
						( \
							select concat('Last Quote @ ', q.currency, ' ', \
								format(q_item.print_rate, %(precision)s)) \
							from `tabQuotation` q, `tabQuotation Item` q_item \
							where \
								q.name = q_item.parent and q_item.item_code = item.name \
								and q.docstatus = 1 and q.customer = \"%(customer)s\" \
							order by q.posting_date desc limit 1 \
						) as quote_rate, \
						( \
							select concat('Last Sale @ ', si.currency, ' ', \
								format(si_item.rate, %(precision)s)) \
							from `tabSales Invoice` si, `tabSales Invoice Item` si_item \
							where \
								si.name = si_item.parent and si_item.item_code = item.name \
								and si.docstatus = 1 and si.customer = \"%(cust)s\" \
							order by si.voucher_date desc limit 1 \
						) as sales_rate, \
						item.item_name, item.description \
					from `tabItem` item \
					where \
						%(condition)s and item.%(key)s like \"%s\" \
					limit 25", {
						customer: me.frm.doc.customer,
						condition: condition,
						precision: precision
					}
				);
			else {
				var query = repl("\
					SELECT name, item_name, description \
					FROM `tabItem` item \
					WHERE %(condition)s and item.%(key)s LIKE '%s' 
					ORDER BY item.item_code DESC LIMIT 50", {condition: condition});
			}
			return query;
		}
	},
})

cur_frm.cscript = new erpnext.selling.Quotation({
	frm: cur_frm, item_table_field: "quotation_items"});










cur_frm.cscript.customer = function(doc,dt,dn) {
	var pl = doc.price_list_name;
	var callback = function(r,rt) {
		var doc = locals[cur_frm.doctype][cur_frm.docname];
		cur_frm.refresh();		
		if (pl != doc.price_list_name) cur_frm.cscript.price_list_name(doc, dt, dn); 
	}

	if(doc.customer) $c_obj(wn.model.get_doclist(doc.doctype, doc.name), 
		'get_default_customer_address', '', callback);
	if(doc.customer) unhide_field(['customer_address','contact_person','territory', 'customer_group']);
}

cur_frm.cscript.pull_enquiry_detail = function(doc,cdt,cdn){
	var callback = function(r,rt){
		if(r.message){
			doc.quotation_to = r.message;

			if(doc.quotation_to == 'Lead') {
					unhide_field('lead');
			}
			else if(doc.quotation_to == 'Customer') {
				unhide_field(['customer','customer_address','contact_person','territory','customer_group']);
			}
			refresh_many(['quotation_details','quotation_to','customer','customer_address','contact_person','lead','lead_name','address_display','contact_display','contact_mobile','contact_email','territory','customer_group','order_type']);
		}
	}

	$c_obj(wn.model.get_doclist(doc.doctype, doc.name),'pull_enq_details','',callback);

}

cur_frm.cscript['Declare Order Lost'] = function(){
	var qtn_lost_dialog;

	set_qtn_lost_dialog = function(doc,cdt,cdn){
		qtn_lost_dialog = new Dialog(400,400,'Add Quotation Lost Reason');
		qtn_lost_dialog.make_body([
			['HTML', 'Message', '<div class="comment">Please add quotation lost reason</div>'],
			['Text', 'Quotation Lost Reason'],
			['HTML', 'Response', '<div class = "comment" id="update_quotation_dialog_response"></div>'],
			['HTML', 'Add Reason', '<div></div>']
		]);

		var add_reason_btn1 = $a($i(qtn_lost_dialog.widgets['Add Reason']), 'button', 'button');
		add_reason_btn1.innerHTML = 'Add';
		add_reason_btn1.onclick = function(){ qtn_lost_dialog.add(); }

		var add_reason_btn2 = $a($i(qtn_lost_dialog.widgets['Add Reason']), 'button', 'button');
		add_reason_btn2.innerHTML = 'Cancel';
		$y(add_reason_btn2,{marginLeft:'4px'});
		add_reason_btn2.onclick = function(){ qtn_lost_dialog.hide();}

		qtn_lost_dialog.onshow = function() {
			qtn_lost_dialog.widgets['Quotation Lost Reason'].value = '';
			$i('update_quotation_dialog_response').innerHTML = '';
		}

		qtn_lost_dialog.add = function() {
			// sending...
			$i('update_quotation_dialog_response').innerHTML = 'Processing...';
			var arg =	strip(qtn_lost_dialog.widgets['Quotation Lost Reason'].value);
			var call_back = function(r,rt) {
				if(r.message == 'true'){
					$i('update_quotation_dialog_response').innerHTML = 'Done';
					qtn_lost_dialog.hide();
				}
			}
			if(arg) $c_obj(wn.model.get_doclist(cur_frm.doc.doctype,
				 cur_frm.doc.name),'declare_order_lost',arg,call_back);
			else msgprint("Please add Quotation lost reason");
		}
	}
	if(!qtn_lost_dialog){
		set_qtn_lost_dialog(doc,cdt,cdn);
	}
	qtn_lost_dialog.show();
}
