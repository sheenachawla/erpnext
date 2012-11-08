wn.require("app/js/mailbox.js");

wn.pages['support-mailbox'].onload = function(wrapper) { 
	wn.ui.make_app_page({
		parent: wrapper,
		title: 'Support Mailbox',
		single_column: true
	});	
	
	erpnext.support_mailbox = new erpnext.MailBox({
		parent: $(wrapper).find(".layout-main")
	});
}