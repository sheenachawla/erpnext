import webnotes
import webnotes.model

def execute():	
	for t in webnotes.conn.sql("""select * from tabTask 
		where ifnull(allocated_to, '')!=''""", as_dict=1):
		
		webnotes.model.insert({
			'doctype':'ToDo',
			'parenttype': "Task",
			'parent': t['name'],
			'owner': t['allocated_to'],
			'assigned_by': t['owner'],
			'description': t['subject'],
			'priority': 'Medium',
			'creation': t['creation']		
		})
