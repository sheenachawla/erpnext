
import webnotes

@webnotes.whitelist()
def get_events():
	import datetime
	
	return webnotes.conn.sql("""select name as `id`, description as title, 
		event_date as `start` from tabEvent 
		where event_date between %s and %s 
		and (event_type='Public' or owner=%s)""", (webnotes.form.start, webnotes.form.end, 
			webnotes.session['user']), as_dict=1)	