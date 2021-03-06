// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd.
// License: GNU General Public License v3. See license.txt

// show tasks
cur_frm.cscript.refresh = function(doc) {
	if(!doc.__islocal) {
		cur_frm.add_custom_button("Gantt Chart", function() {
			wn.route_options = {"project": doc.name}
			wn.set_route("Gantt", "Task");
		}, "icon-tasks");
		cur_frm.add_custom_button("Tasks", function() {
			wn.route_options = {"project": doc.name}
			wn.set_route("List", "Task");
		}, "icon-list");
	}
}

cur_frm.fields_dict.customer.get_query = function(doc,cdt,cdn) {
	return{
		query:"controllers.queries.customer_query"
	}
}