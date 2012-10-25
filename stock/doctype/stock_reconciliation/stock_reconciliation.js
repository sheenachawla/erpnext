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
	if (doc.docstatus) hide_field('steps');
	
	cur_frm.set_intro("");
	
	if(doc.__islocal) {
		cur_frm.set_intro("Step 1: Set the date and time at which you want the balance be set and Save.");
	} else {
		if(!doc.file_list) {
			cur_frm.set_intro("Step 2: Download the template and upload the stock balances.");
			cur_frm.add_custom_button("Upload", function() {
				cur_frm.attachments.new_attachment();
			}, 'icon-upload');
		} else {
			if(doc.docstatus==0) {
				cur_frm.set_intro("Step 3: Now submit the document.");
			}
		}
	}
}

cur_frm.cscript.download_template = function(doc, cdt, cdn) {
	$c_obj_csv(make_doclist(cdt, cdn), 'get_template', '');
}
