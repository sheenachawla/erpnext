cur_frm.cscript.refresh = function(doc) {
	cur_frm.toggle_display('attach', doc.rename_doctype && !doc.file_list);
	cur_frm.toggle_display('rename', doc.file_list);
}

cur_frm.cscript.rename_doctype = function(doc) {
	cur_frm.cscript.refresh(doc);
}

cur_frm.cscript.attach = function(doc) {
	cur_frm.attachments.add_attachment();
}

cur_frm.fields_dict.rename_doctype.get_query = function() {
	return "select name from tabDocType where %(key)s like '%s%%' and ifnull(allow_rename,0)=1"
}