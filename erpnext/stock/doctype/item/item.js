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

cur_frm.cscript.refresh = function(doc) {
	// make sensitive fields(has_serial_no, is_stock_item, valuation_method)
	// read only if any stock ledger entry exists

	if ((!doc.__islocal) && (doc.is_stock_item == 'Yes')) {
		var callback = function(r, rt) {
			if (r.message == 'exists') permlevel = 1;
			else permlevel = 0;

			set_field_permlevel('has_serial_no', permlevel);
			set_field_permlevel('is_stock_item', permlevel);
			set_field_permlevel('valuation_method', permlevel);
		}
		$c_obj(make_doclist(doc.doctype, doc.name),'check_if_sle_exists','',callback);
	}
	
	cur_frm.cscript.hide_website_fields(doc);
}

cur_frm.cscript.hide_website_fields = function(doc) {
	var website_fields_list = ['page_name', 'website_image', 'web_short_description',
								'web_long_description'];
	cur_frm.toggle_display(website_fields_list, cint(doc.show_in_website))
}

cur_frm.cscript.show_in_website = function(doc, dt, dn) {
	cur_frm.cscript.hide_website_fields(doc);
}

cur_frm.cscript.tax_type = function(doc, cdt, cdn){
  var d = locals[cdt][cdn];
  get_server_fields('get_tax_rate',d.tax_type,'item_tax',doc, cdt, cdn, 1);
}


// for description from attachment
// takes the first attachment and creates
// a table with both image and attachment in HTML
// in the "alternate_description" field
cur_frm.cscript.add_image = function(doc, dt, dn) {
	if(!doc.file_list) {
		msgprint('Please attach a file first!');
	}

	var f = doc.file_list.split('\n')[0];
	var fname = f.split(',')[0];
	var fid = f.split(',')[1];
	if(!in_list(['jpg','jpeg','gif','png'], fname.split('.')[1].toLowerCase())) {
		msgprint('File must be of extension jpg, jpeg, gif or png'); return;
	}

	doc.description_html = repl('<table style="width: 100%; table-layout: fixed;">'+
	'<tr><td style="width:110px"><img src="%(imgurl)s" width="100px"></td>'+
	'<td>%(desc)s</td></tr>'+
	'</table>', {imgurl: wn.urllib.get_file_url(fid), desc:doc.description});

	refresh_field('description_html');
}
//===================== Quotation to validation - either customer or lead mandatory ====================
cur_frm.cscript.weight_to_validate = function(doc,cdt,cdn){

  if((doc.nett_weight || doc.gross_weight) && !doc.weight_uom)
  {
    alert('Weight is mentioned,\nPlease mention "Weight UOM" too');
    validated=0;
  }
}
//===================validation function =================================

cur_frm.cscript.validate = function(doc,cdt,cdn){
  cur_frm.cscript.weight_to_validate(doc,cdt,cdn);
}

//===========Fill Default Currency in "Item Prices====================
cur_frm.fields_dict['ref_rate_details'].grid.onrowadd = function(doc, cdt, cdn){
	locals[cdt][cdn].ref_currency = sys_defaults.currency;
	refresh_field('ref_currency',cdn,'ref_rate_details');
}