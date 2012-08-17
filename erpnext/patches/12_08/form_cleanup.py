import webnotes

def execute():
	update_comment()

def update_comment():
	webnotes.conn.sql("""update tabComment set parenttype = comment_doctype,
		parent = comment_docname""")