wn.provide('erpnext.desktop');

erpnext.desktop.gradient = "<style>\
	.case-%(case_class)s {\
		background: %(start)s; /* Old browsers */\
		background: -moz-radial-gradient(center, ellipse cover,  %(start)s 0%, %(middle)s 44%, %(end)s 100%); /* FF3.6+ */\
		background: -webkit-gradient(radial, center center, 0px, center center, 100%, color-stop(0%,%(start)s), color-stop(44%,%(middle)s), color-stop(100%,%(end)s)); /* Chrome,Safari4+ */\
		background: -webkit-radial-gradient(center, ellipse cover,  %(start)s 0%,%(middle)s 44%,%(end)s 100%); /* Chrome10+,Safari5.1+ */\
		background: -o-radial-gradient(center, ellipse cover,  %(start)s 0%,%(middle)s 44%,%(end)s 100%); /* Opera 12+ */\
		background: -ms-radial-gradient(center, ellipse cover,  %(start)s 0%,%(middle)s 44%,%(end)s 100%); /* IE10+ */\
		background: radial-gradient(center, ellipse cover,  %(start)s 0%,%(middle)s 44%,%(end)s 100%); /* W3C */\
	}\
	</style>"

erpnext.desktop.refresh = function() {
	erpnext.desktop.add_classes();
	erpnext.desktop.render();
	
	$("#icon-grid").sortable({
		update: function() {
			new_order = [];
			$("#icon-grid .case-wrapper").each(function(i, e) {
				new_order.push($(this).attr("data-name"));
			});
			wn.user.set_default("_desktop_items", new_order);
		}
	});
}

erpnext.desktop.add_classes = function() {
	$.each(wn.meta.get("Desktop Item"), function(i, v) {
		var g = v.gradient.split(",");
		v.start = g[0];
		v.middle = g[1];
		v.end = g[2];
		v.case_class = v.label.replace(/ /g, "_").toLowerCase();
		$(repl(erpnext.desktop.gradient, v)).appendTo('head');
	});
}

erpnext.desktop.render = function() {
	var add_icon = function(desktop_item) {
		desktop_item._label = wn._(desktop_item.label);
		$('#icon-grid').append(repl('\
			<div id="%(case_class)s" class="case-wrapper" data-name="%(name)s">\
				<a href="#%(route)s">\
					<div class="case-border case-%(case_class)s">\
						<div class="sprite-image sprite-%(style)s"></div>\
					</div>\
				</a>\
				<div class="case-label">%(_label)s</div>\
			</div>', desktop_item));	
	}
	
	// setup
	$.each(wn.user.get_desktop_items(), function(i, d) {
		add_icon(d);
	})

	// apps
	erpnext.desktop.show_pending_notifications();

}

erpnext.desktop.show_pending_notifications = function() {
	var add_circle = function(str_module, id, title) {
		var module = $('#'+str_module);
		module.find('a:first').append(
			repl('<div id="%(id)s" class="circle" title="%(title)s" style="display: None">\
					<span class="circle-text"></span>\
				 </div>', {id: id, title: title}));
		
		var case_border = module.find('.case-border');
		var circle = module.find('.circle');

		var add_hover_and_click = function(primary, secondary, hover_class, click_class) {
			primary
			.hover(
				function() { secondary.addClass(hover_class); },
				function() { secondary.removeClass(hover_class); })
			.mousedown(function() { secondary.addClass(click_class); })
			.mouseup(function() { secondary.removeClass(click_class); })
			.focusin(function() { $(this).mousedown(); })
			.focusout(function() { $(this).mouseup(); })
		}
		
		add_hover_and_click(case_border, circle, 'hover-effect', 'circle-click');
		add_hover_and_click(circle, case_border, 'hover-effect', 'case-border-click');

	}

	add_circle('messages', 'unread_messages', 'Unread Messages');
	add_circle('support', 'open_support_tickets', 'Open Support Tickets');
	add_circle('to_do', 'things_todo', 'Things To Do');
	add_circle('calendar', 'todays_events', 'Todays Events');
	add_circle('projects', 'open_tasks', 'Open Tasks');
	add_circle('knowledge_base', 'unanswered_questions', 'Unanswered Questions');

	erpnext.update_messages();

}

pscript.onload_desktop = function() {
	// load desktop
	erpnext.desktop.refresh();
}

