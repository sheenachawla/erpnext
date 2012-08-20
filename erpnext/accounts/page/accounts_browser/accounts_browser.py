from __future__ import unicode_literals
import webnotes
from webnotes.utils import cstr, nowdate

@webnotes.whitelist()
def get_companies():
	return [r[0] for r in webnotes.connn.sql("""select name from tabCompany where docstatus!=2""")]
	
@webnotes.whitelist()
def get_children():
	args = webnotes.form
	ctype, company = args['ctype'], args['comp']
	
	company_field = ctype=='Account' and 'company' or 'company_name'

	# root
	if args['parent'] == company:
		acc = webnotes.conn.sql(""" select 
			name as value, if(group_or_ledger='Group', 1, 0) as expandable
			from `tab%s`
			where ifnull(parent_%s,'') = ''
			and %s = %s	and docstatus<2 
			order by name""" % (ctype, ctype.lower().replace(' ','_'), company_field, '%s'),
				args['parent'], as_dict=1)
	else:	
		# other
		acc = webnotes.conn.sql("""select 
			name as value, if(group_or_ledger='Group', 1, 0) as expandable
	 		from `tab%s` 
			where ifnull(parent_%s,'') = %s
			and docstatus<2 
			order by name""" % (ctype, ctype.lower().replace(' ','_'), '%s'),
				args['parent'], as_dict=1)
				
	if ctype == 'Account':
		currency = webnotes.conn.get_value('Company', company, 'default_currency')
		import accounts.utils
		for each in acc:
			bal = accounts.utils.get_balance_on(each.get('value'), nowdate)
			each['balance'] = currency + ' ' + cstr(bal)
	return acc
