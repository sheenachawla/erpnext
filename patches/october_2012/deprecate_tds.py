def execute():
	import webnotes
	from webnotes.model import delete_doc
	from webnotes.model.code import get_obj
	from webnotes.model.doc import addchild
	
	# delete doctypes and tables
	for dt in ["TDS Payment", "TDS Return Acknowledgement", "Form 16A", 
			"TDS Rate Chart", "TDS Category", "TDS Control"]:
		delete_doc("DocType", dt)
		webnotes.conn.sql("drop table if exists `tab%s`" % dt)
		
		for child_dt in webnotes.model.meta.get_table_fields(dt):
			webnotes.conn.sql("drop table if exists `tab%s`" % child_dt[0])
			
	delete_doc("Search Criteria", "tds_return")
			
	# Add tds entry in tax table for purchase invoice
	pi_list = webnotes.conn.sql("""select name from `tabPurchase Invoice` 
		where ifnull(tax_code, '')!='' and ifnull(ded_amount)!=0""")
	for pi in pi_list:
		piobj = get_obj("Purchase Invoice", pi[0], with_children=1)
		ch = addchild(piobj.doc, 'purchase_tax_details', 'Purchase Taxes and Charges')
		ch.charge_type = "Actual"
		ch.account_head = piobj.doc.tax_code
		ch.description = piobj.doc.tax_code
		ch.rate = -1*piobj.doc.ded_amount
		ch.tax_amount = -1*piobj.doc.ded_amount
		ch.category = "Total"
		ch.save(1)
		
		piobj.calculate_taxes_and_totals()
		
	
	# Add tds entry in entries table for journal voucher
	jv_list = webnotes.conn.sql("""select name from `tabJournal Voucher` 
		where ifnull(tax_code, '')!='' and ifnull(ded_amount)!=0""")
	for jv in jv_list:
		jvobj = get_obj("Journal Voucher", jv[0], with_children=1)
		ch = addchild(jvobj.doc, 'entries', 'Journal Voucher Detail')
		ch.account = jvobj.doc.tax_code
		ch.credit = jvobj.doc.ded_amount
		ch.save(1)
		
		
		