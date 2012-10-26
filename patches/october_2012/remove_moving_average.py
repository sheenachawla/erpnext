def execute():
	import webnotes
	webnotes.conn.sql("""delete from `tabDefaultValue` 
		where defkey in ('valuation_method', 'stock_valuation'""")
		
