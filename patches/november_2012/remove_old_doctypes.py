import webnotes

def execute():
	from webnotes.model import delete_doc
	removed_list = ['Form 16A', 'Form 16A Ack Detail', 'Form 16A Tax Detail', 
		'RV Detail', 'TDS Category', 'TDS Category Account', 'TDS Control', 
		'TDS Detail', 'TDS Payment', 'TDS Payment Detail', 'TDS Rate Chart', 
		'TDS Rate Detail', 'TDS Return Acknowledgement', 'Company Control', 
		'Home Control', 'Library', 'Update Delivery Date', 'Project Activity', 
		'Project Activity Update', 'Project Control', 'Communication Log', 
		'Plot Control', 'Shipping Address', 'Manage Account', 'Valuation Control', 
		'Menu Control', 'Blog Subscriber', 'Product', 'Product Group', 
		'Products Settings', 'Doctype Label']
		
	for doctype in removed_list:
		delete_doc("DocType", doctype)
		
	remove_pages = ['accounts-home', 'buying-home', 'hr-home', 'production-home',
		'projects-home', 'selling-home', 'stock-home', 'support-home', 'website-home'
		'Sales Dashboard', 'Webforms', 'WIP Monitor', 'My Company', 'dashboard']

	for page in remove_pages:
		delete_doc("Page", page)
