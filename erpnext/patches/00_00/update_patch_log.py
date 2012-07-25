# This patch will get executed while merging testcases branch

def execute():
	import webnotes
	
	from webnotes.utils import set_default, get_defaults
	if not get_defaults('patch_version'):
		set_default('patch_version', '00_00')
	
	repl = [
		['before_jan_2012', '00_00'], 
		['jan_mar_2012', '12_03'], 
		['mar_2012', '12_03'],
		['april_2012', '12_04'],
		['may_2012', '12_05'],
		['june_2012', '12_06'],
		['july_2012', '12_07']
	]
	for d in repl:
		webnotes.conn.sql("update `__PatchLog` set patch = replace(patch, %s, %s)", (d[0], d[1]))