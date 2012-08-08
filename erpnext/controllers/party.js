cur_frm.cscript.make_address = function() {
	if(!cur_frm.address_list) {
		cur_frm.address_list = new wn.ui.Listing({
			parent: cur_frm.fields_dict['address_html'].wrapper,
			page_length: 2,
			new_doctype: "Address",
			get_query: function() {
				return "select name, address_type, address_line1, address_line2, city, \
				state, country, pincode, fax, email_id, phone, is_primary_address, \
				is_shipping_address from tabAddress \
				where "+cur_frm.doctype.toLowerCase() +"='"+cur_frm.docname+"' \
				and docstatus != 2 order by is_primary_address desc"
			},
			as_dict: 1,
			no_results_message: 'No addresses created',
			render_row: cur_frm.cscript.render_address_row,
		});
		// note: render_address_row is defined in contact_control.js
	}
	cur_frm.address_list.run();
}



cur_frm.cscript.make_contact = function() {
	if(!cur_frm.contact_list) {
		cur_frm.contact_list = new wn.ui.Listing({
			parent: cur_frm.fields_dict['contact_html'].wrapper,
			page_length: 2,
			new_doctype: "Contact",
			get_query: function() {
				return "select name, first_name, last_name, email_id, phone, mobile_no, \
				department, designation, is_primary_contact from tabContact \
				where "+cur_frm.doctype.toLowerCase() +"='"+cur_frm.docname+"' and docstatus != 2 \
				order by is_primary_contact desc"
			},
			as_dict: 1,
			no_results_message: 'No contacts created',
			render_row: cur_frm.cscript.render_contact_row,
		});
		// note: render_contact_row is defined in contact_control.js
	}
	cur_frm.contact_list.run();
}