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
		title: wn._(module),
		single_column: true
	});

	wn.call({
		method: 'core.doctype.module_def.module_def.get_items',
		args: {
			module: module
		},
		callback: function(r) {
			items = r.message;
			make_section('transaction', wn._("Transactions"));
			make_section('master', wn._("Masters"));
			make_section('tool', wn._("Tools"));
			make_section('setup', wn._("Setup"));
			make_section('report', wn._("Report"));
		}
	})
	
	var make_section = function(name, title) {
		if(!items[name].length) return;
		
		$(repl('<h4>%(title)s</h4><br><div class="%(name)s"></div><hr>', {title: title, name: name}))
			.appendTo($(wrapper).find('.layout-main'));
		
		var $body = $(wrapper).find('.' + name);
		
		// get maxx
		var maxx = Math.max.apply(this, $.map(items[name], function(v) {
			if(v[0]=='DocType') {
				var m = 0;
				$.each(v[2], function(i,count) { m=m+count });
				return m;
			};
		}));
				
		// items
		$.each(items[name], function(i, v) {
			make_item($body, v, name, parseInt(maxx));
		});
	}
	
	var make_item = function(parent, v, section_name, maxx) {
		var icons = {
			"DocType": "icon-pencil",
			"Single": "icon-cog",
			"Page": "icon-cog",
			"Report": "icon-th"
		};
		if(section_name=='master') {
			icons.DocType = "icon-flag";
		}
				
		var routes = {
			"DocType": "#List/%(name)s",
			"Single": "#Form/%(name)s",
			"Page": "#%(name)s",
			"Report": "#Reports/%(doctype)s/%(name)s"
		}
				
		var progress = '';
		if(v[0]=='DocType' && maxx!=NaN) {
			var progress = repl('<div style="width: 60%; float: left;">\
				<div class="progress" style="width: 80%; float: left;">\
					<div class="bar bar-info" style="width: %(ds_0)s%"></div>\
					<div class="bar bar-success" style="width: %(ds_1)s%"></div>\
					<div class="bar bar-danger" style="width: %(ds_2)s%"></div>\
				</div> <div style="float: left; margin-left: 7px;">(%(maxx)s)</div>\
			</div>', {
				ds_0: v[2][0] / maxx * 100,
				ds_1: v[2][1] / maxx * 100,
				ds_2: v[2][2] / maxx * 100,
				maxx: v[2][0] + v[2][1] + v[2][2]
			});
		} 
		
		$(repl('<div style="margin: 6px 0px; min-height: 40px;"> <div style="width: 30%; float: left;">\
			<i class="icon %(icon)s"></i>\
			<b><a href="%(route)s">%(title)s</a></b></div>\
			%(progress)s\
			<div style="clear: both;"></div>\
			</div>', {
				icon: icons[v[0]],
				title: wn._(v[1]),
				progress: progress,
				route: repl(routes[v[0]], {name: v[1], doctype: v[2]})
			})).appendTo(parent);
	}
}