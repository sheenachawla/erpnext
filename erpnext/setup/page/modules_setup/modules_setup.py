from __future__ import unicode_literals
import webnotes

@webnotes.whitelist()
def update(arg=None):
	"""update modules"""
	webnotes.conn.set_global('modules_list', webnotes.form['ml'])
	webnotes.msgprint('Updated')
	
	import webnotes.session_cache
	webnotes.session_cache.clear_cache()