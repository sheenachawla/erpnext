# ERPNext - web based ERP (http://erpnext.com)
# Copyright (C) 2012 Web Notes Technologies Pvt Ltd
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# html generation functions

template_map = {
	'Web Page': 'html/web_page.html',
	'Blog': 'html/blog_page.html',
	'Item': 'html/product_page.html',
}

import conf

def get_html(session, page_name, comments=''):
	html = ''
	
	# load from cache, if auto cache clear is falsy
	if not (hasattr(conf, 'auto_cache_clear') and conf.auto_cache_clear or 0):
		html = session.memc.get_value("page:" + page_name)

	if not html:
		html = load_into_cache(session, page_name)
		comments += "\n\npage load status: fresh"
	
	# insert comments
	import webnotes.utils
	html += """\n<!-- %s -->""" % webnotes.utils.cstr(comments)
	
	return html

def load_into_cache(session, page_name):
	html = build_html(prepare_args(session, page_name))	
	session.memc.set_value("page:" + page_name, html)
	return html

def get_predefined_pages():
	"""gets a list of predefined pages, they do not exist in `tabWeb Page`"""
	import os
	import conf
	import website.utils
	
	pages_path = os.path.join(conf.modules_path, 'website', 'templates', 'pages')
	
	page_list = []
	
	for page in os.listdir(pages_path):
		page_list.append(website.utils.scrub_page_name(page))

	return page_list

def prepare_args(session, page_name):
	import webnotes
	if page_name == 'index':
		page_name = session.bootinfo.home_page
	
	if page_name in get_predefined_pages():
		args = {
			'template': 'pages/%s.html' % page_name,
			'name': page_name,
			'session': session
		}
	else:
		args = get_doc_fields(session, page_name)
	
	args.update(get_outer_env(session))
	
	return args

def get_doc_fields(session, page_name):
	doctype, name = get_source_doc(session, page_name)
	
	if not doctype:
		raise Exception, "Page %s not found" % page_name
		
	con = session.controller(doctype, name)
		
	if hasattr(con, 'prepare_template_args'):
		con.prepare_template_args()
		
	args = con.doc
	args['template'] = template_map[doctype]
	
	return args
	
def get_source_doc(session, page_name):
	"""get source doc for the given page name"""
	for doctype in ['Web Page', 'Blog', 'Item']:		
		name = session.db.sql("""select name from `tabWeb Page` where page_name=%s""", page_name)
		if name:
			return doctype, name[0][0]
			
	return None, None

def get_outer_env(session):
	"""env dict for outer.html template"""
	all_top_items = session.db.sql("""\
		select * from `tabTop Bar Item`
		where parent='Website Settings' and parentfield='top_bar_items'
		order by idx asc""", as_dict=1)
		
	top_items = [d for d in all_top_items if not d['parent_label']]
	
	# attach child items to top bar
	for d in all_top_items:
		if d['parent_label']:
			for t in top_items:
				if t['label']==d['parent_label']:
					if not 'child_items' in t:
						t['child_items'] = []
					t['child_items'].append(d)
					break
	
	return {
		'top_bar_items': top_items,
	
		'footer_items': session.db.sql("""\
			select * from `tabTop Bar Item`
			where parent='Website Settings' and parentfield='footer_items'
			order by idx asc""", as_dict=1),
			
		'brand': session.db.get_value('Website Settings', None, 'brand_html') or 'ERPNext',
		'copyright': session.db.get_value('Website Settings', None, 'copyright'),
		'favicon': session.db.get_value('Website Settings', None, 'favicon')
	}
	
def build_html(args):
	"""build html using jinja2 templates"""
	import os
	import conf
	templates_path = os.path.join(conf.modules_path, 'website', 'templates')
	
	from jinja2 import Environment, FileSystemLoader
	jenv = Environment(loader = FileSystemLoader(templates_path))
	html = jenv.get_template(args['template']).render(args)
	return html

def clear_cache(session, page_name, doc_type=None, doc_name=None):
	"""
		* if no page name, clear whole cache
		* if page_name, doc_type and doc_name match, clear cache's copy
		* else, raise exception that such a page already exists
	"""
	import webnotes

	if page_name:
		session.memc.delete_value("page:" + page_name)
	else:
		session.memc.flush_keys("page:")
	
def delete_page_cache(session, page_name):
	"""
		delete entry of page_name from Web Cache
		used when:
			* web page is deleted
			* blog is un-published
	"""
	session.memc.delete_value("page:" + page_name)