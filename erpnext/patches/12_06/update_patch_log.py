# This patch will get executed while merging scrap_msql branch
# Don't put it into patch_list
# Run as a separate patch

def execute():
	import webnotes
	
	from webnotes.utils import set_default
	set_default('patch_module', '12_03')
	
	repl = [
		['before_jan_2012', '00_00'], 
		['jan_mar_2012', '12_03'], 
		['mar_2012', '12_03'],
		['apr_2012', '12_04'],
		['may_2012', '12_05'],
		['june_2012', '12_06']
	]
	for d in repl:
		webnotes.conn.sql("update `__PatchLog` set patch = replace(patch, %s, %s)", (d[0], d[1]))