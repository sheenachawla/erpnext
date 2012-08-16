from __future__ import unicode_literals
import webnotes

def execute():
	remove_doctypes()
	
def remove_doctypes():
	from webnotes.model import delete_doc
	dt_list = ['Account Balance', 'Period', 'Reposting Tool', 'Lease Agreement', 'Lease Installment']
	for dt in dt_list:
		delete_doc('DocType', dt)
		webnotes.conn.commit()
		webnotes.conn.sql("drop table if exists `tab%s`" % dt)
		webnotes.conn.begin()
		
def set_fy_end_date():
	for fy in webnotes.conn.sql("select name, year_start_date, year_end_date from `tabFiscal Year`", as_dict=1):
		if not fy['year_end_date']:
			end_date = get_last_day(get_first_day(fy['year_start_date'],0,11)).strftime('%Y-%m-%d')
			webnotes.conn.set_value('Fiscal Year', fy['name'], 'year_end_date', end_date)
			
