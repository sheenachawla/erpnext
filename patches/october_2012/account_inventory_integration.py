import webnotes

def execute():
	insert_accounts()
	
def insert_accounts():
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
				make_account_dict('Expenses Included In Valuation', 'Stock Expenses', 
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
	
def set_accounts():
	pr_amount = webnotes.conn.sql("""select sum(amount) from `tabPurchase Receipt Item` as pr_item 
		where docstatus=1 and exists(select name from tabItem where name = pr_item.item_code and 
		ifnull(is_stock_item, 'No')='Yes')""")[0][0]
			
	pi_amount = webnotes.conn.sql("""select sum(amount) from `tabPurchase Invoice Item` as pi_item 
		where docstatus=1 and ifnull(purchase_receipt, '')!='' 
		and exists(select name from tabItem where name = pi_item.item_code and 
		ifnull(is_stock_item, 'No')='Yes')""")[0][0]
	
	stock_received_but_not_billed = pr_amount - pi_amount
	
	dn_amount = webnotes.conn.sql("""select sum(amount) from `tabDelivery Note Item` as dn_item 
		where docstatus=1 and exists(select name from tabItem where name = dn_item.item_code and 
		ifnull(is_stock_item, 'No')='Yes')""")[0][0]
			
	si_amount = webnotes.conn.sql("""select sum(amount) from `tabSales Invoice Item` as si_item 
		where docstatus=1 and ifnull(delivery_note, '')!='' 
		and exists(select name from tabItem where name = si_item.item_code and 
		ifnull(is_stock_item, 'No')='Yes')""")[0][0]
	
	stock_delivered_but_not_billed = dn_amount - si_amount
	
	gl_entries = []
	from controllers.accounts_controller import *
	stock_in_hand = get_stock_in_hand_account()
	
	gl_entries.append(
		get_gl_dict({
			"account": stock_in_hand,
			"against": "Stock Received But Not Billed - %s" % abbr,
			"debit": stock_received_but_not_billed - stock_delivered_but_not_billed,
			"remarks": "Opening Entry for Stock Received But Not Billed"
		}, cancel)
	)

	# stock received but not billed
	gl_entries.append(
		self.get_gl_dict({
			"account": "Stock Received But Not Billed - %s" % abbr,
			"against": stock_in_hand,
			"credit": stock_received_but_not_billed,
			"remarks": "Opening Entry for Stock Received But Not Billed"
		}, cancel)
	)
	# stock delivered but not billed
	gl_entries.append(
		self.get_gl_dict({
			"account": "Stock Delivered But Not Billed - %s" % abbr,
			"against": stock_in_hand,
			"credit": stock_delivered_but_not_billed,
			"remarks": "Opening Entry for Stock Delivered But Not Billed"
		}, cancel)
	)
	
	make_gl_entries(gl_map=gl_entries)