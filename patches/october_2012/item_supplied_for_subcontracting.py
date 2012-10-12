import webnotes
def execute():
	new_dt = "Items Supplied For Subcontracting"
	new_fields = [d[0] for d in
		webnotes.conn.sql("""desc `tab%s`""" % new_dt)]
	
	for tab in ["Purchase Order Item Supplied", "Purchase Receipt Item Supplied"]:
		old_fields = [d[0] for d in webnotes.conn.sql("""desc `tab%s`""" % tab)]

		valid_fields = list(set(new_fields) & set(old_fields))
		valid_fields_repr = "`" + "`, `".join(valid_fields) + "`"

		query = """insert into `tab%s`(%s)
			(select %s from `tab%s`)""" % (new_dt, valid_fields_repr, 
			valid_fields_repr, tab)
		webnotes.conn.sql(query)
		
		webnotes.conn.sql("""update `tab%s` 
			set parentfield='items_supplied_for_subcontracting'""" % new_dt)
	
	from webnotes.model import delete_doc
	for tab in ["Purchase Order Item Supplied", "Purchase Receipt Item Supplied"]:
		delete_doc("DocType", tab)
		webnotes.conn.commit()
		webnotes.conn.sql("""drop table `tab%s`""" % tab)
		webnotes.conn.begin()