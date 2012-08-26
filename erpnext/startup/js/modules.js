// ERPNext - web based ERP (http://erpnext.com)
// Copyright (C) 2012 Web Notes Technologies Pvt Ltd
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

wn.provide('erpnext.module_page');

erpnext.module_page.make = function(module, wrapper) {
	var items = {};
	wn.ui.make_app_page({
		parent: wrapper,
		title: module,
		single_column: true
	});

	wn.call({
		method: 'core.doctype.module_def.module_def.get_items',
		args: {
			module: module
		},
		callback: function(r) {
			items = r.message;
			make_section('transaction');
			make_section('master');
			make_section('tool');
			make_section('setup');
			make_section('report');
		}
	})
	
	var make_section = function(name) {
		if(!items[name].length) return;
		
		$(repl('<h4>%(title)s</h4><ul class="%(name)s"></ul><hr>', {title: toTitle(name), name: name}))
			.appendTo($(wrapper).find('.layout-main'));
			
		// items
		$.each(items[name], function(i, v) {
			if(v[0]=='DocType') {
				$(repl('<li><a href="#List/%(name)s">%(name)s</a></li>', {name: v[1]}))
					.appendTo($(wrapper).find('.' + name));
			} else if(v[0]=='Report') {
				$(repl('<li><a href="#Report/%(doctype)s/%(name)s">%(name)s</a></li>', 
					{name: v[1], doctype:v[2]}))
					.appendTo($(wrapper).find('.' + name));				
			}
		})
	}
}