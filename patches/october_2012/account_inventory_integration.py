def execute():
	import webnotes
	from webnotes.model import insert
	for d in webnotes.conn.sql("""select name, abbr from tabCompany""", as_dict=1):
		acc_list = [
			make_account_dict('Stock Assets', 'Current Assets', d, 'Group'),
				make_account_dict('Stock In Hand', 'Stock Assets', d, 'Ledger'),
				make_account_dict('Stock Delivered But Not Billed', 'Stock Assets', 
					d, 'Ledger'),
			make_account_dict('Stock Liabilities', 'Current Liabilities', d, 'Group'),
				make_account_dict('Stock Received But Not Billed', 'Stock Liabilities',
				 	d, 'Ledger'),
			make_account_dict('Stock Expenses', 'Direct Expenses', d, 'Group'),
				make_account_dict('Stock Variance', 'Stock Expenses', d, 'Ledger'),
				make_account_dict('Valuation Price Difference', 'Stock Expenses', 
					d, 'Ledger'),
		]
		for acc in acc_list:
			acc_name = "%s - %s" % (acc['account_name'], d['abbr'])
			if not webnotes.conn.exists('Account', acc_name):
				insert(acc)
			else:
				print "Account %s already exists" % acc_name
		
def make_account_dict(account, parent, company_detail, group_or_ledger):
	return {
		"doctype": "Account",
		"account_name": account,
		"parent_account": "%s - %s" % (parent, company_detail['abbr']),
		"company": company_detail['name'],
		"group_or_ledger": group_or_ledger
	}
	