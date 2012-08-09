from __future__ import unicode_literals
import webnotes

@webnotes.whitelist()
def get_children():
	ctype = webnotes.form.get('ctype')
	webnotes.form['parent_field'] = 'parent_' + ctype.lower().replace(' ', '_')
	
	return webnotes.conn.sql("""select name as value, 
		if(is_group='Yes', 1, 0) as expandable
		from `tab%(ctype)s`
		where docstatus < 2
		and %(parent_field)s = "%(parent)s"
		order by name""" % webnotes.form, as_dict=1)
		
@webnotes.whitelist()
def add_node():
	from webnotes.model.doc import Document
	ctype = webnotes.form.get('ctype')
	parent_field = 'parent_' + ctype.lower().replace(' ', '_')

	d = Document(ctype)
	d.fields[ctype.lower().replace(' ', '_') + '_name'] = webnotes.form['name_field']
	d.fields[parent_field] = webnotes.form['parent']
	d.is_group = webnotes.form['is_group']
	d.save()