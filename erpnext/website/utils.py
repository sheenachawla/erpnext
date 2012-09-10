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

import webnotes, os

def scrub_page_name(page_name):
	if page_name.endswith('.html'):
		page_name = page_name[:-5]

	return page_name

def make_template(doc, path, convert_fields = ['main_section', 'side_section']):
	"""make template"""
	import os, jinja2
	
	markdown(doc, convert_fields)
	
	# write template
	with open(path, 'r') as f:
		temp = jinja2.Template(f.read())
	
	return temp.render(doc = doc)

def page_name(title):
	"""make page name from title"""
	if not title: return
	
	import re
	name = title.lower()
	name = re.sub('[~!@#$%^&*()<>,."\']', '', name)
	return '-'.join(name.split()[:4])

def render(session, page_name):
	"""render html page"""
	import webnotes
	try:
		html = get_html(session, page_name or 'index')
	except Exception, e:
		html = get_html(session, '404')

	return html
	
def get_html(session, page_name):
	"""get page html"""
	page_name = scrub_page_name(page_name)
	comments = get_comments(page_name)
	
	import website.web_cache
	html = website.web_cache.get_html(session, page_name, comments)
	return html

def get_comments(page_name):
	import webnotes.utils
	
	if page_name == '404':
		comments = """error: %s""" % webnotes.utils.getTraceback()
	else:
		comments = """page: %s""" % page_name
		
	return comments	

def make_web_files(session):
	"""make index.html, wn-web.js, wn-web.css, sitemap.xml and rss.xml"""	
	home_page = session.db.get_value('Website Settings', None, 'home_page')

	# script - wn.js
	import startup.event_handlers

	fname = 'js/wn-web.js'
	if os.path.basename(os.path.abspath('.'))!='public':
		fname = os.path.join('public', fname)
			
	with open(fname, 'w') as f:
		script = 'window.home_page = "%s";\n' % home_page
		script += session.db.get_value('Website Settings', None, 'startup_code') or ''
			
		f.write(script)

	fname = 'css/wn-web.css'
	if os.path.basename(os.path.abspath('.'))!='public':
		fname = os.path.join('public', fname)

	# style - wn.css
	with open(fname, 'w') as f:
		f.write(session.db.get_value('Style Settings', None, 'custom_css') or '')