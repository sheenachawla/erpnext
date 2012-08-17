
/*
 *	lib/js/legacy/widgets/report_builder/report_builder.js
 */
// Copyright (c) 2012 Web Notes Technologies Pvt Ltd (http://erpnext.com)
// 
// MIT License (MIT)
// 
// Permission is hereby granted, free of charge, to any person obtaining a 
// copy of this software and associated documentation files (the "Software"), 
// to deal in the Software without restriction, including without limitation 
// the rights to use, copy, modify, merge, publish, distribute, sublicense, 
// and/or sell copies of the Software, and to permit persons to whom the 
// Software is furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in 
// all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
// PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
// CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
// OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
// 

// ReportContainer Contains ReportBuilder objects for all DocTypes
//  - Only one ReportContainer exists
//  - Page header is als a part
//  - New ReportBuilder is made here

_r.ReportContainer = function() {
	if(user=='Guest') {
		msgprint("Not Allowed");
		return;
	}
	var page = wn.container.add_page("Report Builder");
	this.wrapper = $a(page, 'div', 'layout-wrapper', {padding: '0px'});
	this.appframe = new wn.ui.AppFrame(this.wrapper);
	this.appframe.$titlebar.append('<span class="report-title">');
	this.rb_area = $a(this.wrapper, 'div', '', {padding: '15px'});
			
	var me = this;
	this.rb_dict = {};


	var run_fn = function() { 
		if(me.cur_rb){
			me.cur_rb.dt.start_rec = 1;
			me.cur_rb.dt.run();
		} 
	}
	
	var runbtn = this.appframe.add_button('Run', run_fn, 'icon-refresh');

	// refresh btn
	this.appframe.add_button('Export', function() { me.cur_rb && me.cur_rb.dt.do_export(); },
		'icon-download-alt');
	this.appframe.add_button('Print', function() { me.cur_rb && me.cur_rb.dt.do_print(); },
		'icon-print');
	this.appframe.add_button('Calc', function() { me.cur_rb && me.cur_rb.dt.do_calc(); },
		'icon-plus');
	
	// new
	if(has_common(['Administrator', 'System Manager'], user_roles)) {
		// save
		
		var savebtn = this.appframe.add_button('Save', 
			function() {if(me.cur_rb) me.cur_rb.save_criteria(); });
		
		// advanced
		var fn = function() { 
			if(me.cur_rb) {
				if(!me.cur_rb.current_loaded) {
					msgprint("error:You must save the report before you can set Advanced features");
					return;
				}
				loaddoc('Search Criteria', me.cur_rb.sc_dict[me.cur_rb.current_loaded]);
			}
		};
		var advancedbtn = this.appframe.add_button('Advanced Settings', fn, 'icon-cog');
	}
	
	// set a type
	this.set_dt = function(dt, onload) {
		my_onload = function(f) {
			if(!f.forbidden) {
				me.cur_rb = f;
				me.cur_rb.mytabs.items['Result'].expand();
				if(onload)onload(f);
			}
		}
	
		if(me.cur_rb)
			me.cur_rb.hide();
		if(me.rb_dict[dt]){
			me.rb_dict[dt].show(my_onload);
		} else {
			me.rb_dict[dt] = new _r.ReportBuilder(me.rb_area, dt, my_onload);
		}

	}
}

// ===================================================================================
// + ReportBuilder
//      + Datatable (grid)
//      + ColumnPicker
//      + ReportFilter
//
// - Contains all methods relating to saving, loading and executing Search Criteria
// - Contains ui objects of the report including tabs

_r.ReportBuilder = function(parent, doctype, onload) {
	this.menuitems = {};
	this.has_primary_filters = false;
	this.doctype = doctype;
	this.forbidden = 0;

	this.filter_fields = [];
	this.filter_fields_dict = {};
	
	var me = this;

	this.fn_list = ['beforetableprint','beforerowprint','afterrowprint','aftertableprint','customize_filters','get_query'];

	this.wrapper = $a(parent, 'div', 'finder_wrapper');

	this.make_tabs();
	this.current_loaded = null;
	this.setup_doctype(onload);
	
	this.hide = function() {
		$dh(me.wrapper);
	}
	this.show = function(my_onload) {
		$ds(me.wrapper);
		
		// reset main title
		this.set_main_title('Report: ' + get_doctype_label(me.doctype));
		
		if(my_onload)my_onload(me);
	}
	
}

// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.make_tabs = function() {
	this.tab_wrapper = $a(this.wrapper, 'div', 'finder_tab_area');
	this.mytabs = new TabbedPage(this.tab_wrapper);
	
	this.mytabs.add_item('Result', null, null, 1);
	this.mytabs.add_item('More Filters', null, null, 1);
	this.mytabs.add_item('Select Columns', null, null, 1);
	
	this.mytabs.tabs = this.mytabs.items;
}

// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.make_body = function() {

	this.set_main_title('Report: ' + get_doctype_label(this.doctype));
	var me = this;

	this.make_save_criteria();	
	this.column_picker = new _r.ReportColumnPicker(this);
	this.report_filters = new _r.ReportFilters(this);
}

//
// Make list of all Criterias relating to this DocType
// -------------------------------------------------------------------------------------
// Search Criterias are loaded with the DocType - put them in a list and dict

_r.ReportBuilder.prototype.make_save_criteria = function() {
	var me = this;
	
	// make_list
	// ---------
	this.sc_list = []; this.sc_dict = {};
	for(var n in locals['Search Criteria']) {
		var d = locals['Search Criteria'][n];
		if(d.doc_type==this.doctype) {
			this.sc_list[this.sc_list.length] = d.criteria_name;
			this.sc_dict[d.criteria_name] = n;
		}
	}
}

// Save Criteria
// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.save_criteria = function(save_as) {
	var overwrite = 0;
	// is loaded?
	if(this.current_loaded && (!save_as)) {
		var overwrite = confirm('Do you want to overwrite the saved criteria "'+this.current_loaded+'"');
		if(overwrite) {
			var doc = locals['Search Criteria'][this.sc_dict[this.current_loaded]];
			var criteria_name = this.current_loaded;
		}
	}

	// new criteria
	if(!overwrite) {
		var criteria_name = prompt('Select a name for the criteria:', '');
		if(!criteria_name)
			return;
	
		var dn = createLocal('Search Criteria');
		var doc = locals['Search Criteria'][dn];

		doc.criteria_name = criteria_name;
		doc.doc_type = this.doctype;
	}

	var cl = []; var fl = {};
	
	// save columns
	var t = this.column_picker.get_selected();
	for(var i=0;i<t.length;i++)
		cl.push(t[i].parent + '\1' + t[i].label);
		
	// save filters
	for(var i=0;i<this.filter_fields.length;i++) {
		var t = this.filter_fields[i];
		var v = t.get_value?t.get_value():'';
		if(v) fl[t.df.parent + '\1' + t.df.label + (t.bound?('\1'+t.bound):'')] = v;
	}
	
	doc.columns = cl.join(',');
	doc.filters = JSON.stringify(fl);
	
	// sort by and sort order
	doc.sort_by = sel_val(this.dt.sort_sel);
	doc.sort_order = this.dt.sort_order;
	doc.page_len = this.dt.page_len;
	
	// save advanced
	if(this.parent_dt)
		doc.parent_doc_type = this.parent_dt
	
	// rename
	var me = this;
	var fn = function(r) {
		me.sc_dict[criteria_name] = r.main_doc_name;
		me.set_criteria_sel(criteria_name);
	}
	//if(this.current_loaded && overwrite) {
	//	msgprint('Filters and Columns Synchronized. You must also "Save" the Search Criteria to update');
	//	loaddoc('Search Criteria', this.sc_dict[this.current_loaded]);
	//} else {
	save_doclist(doc.doctype, doc.name, 'Save', fn); // server-side save
	//}
}

// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.hide_all_filters = function() {
	for(var i=0; i<this.filter_fields.length; i++) {
		this.filter_fields[i].df.filter_hide = 1;
	}
}

// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.run = function() {
	// Note: all client code is executed in datatable
	this.dt.run();
}

// Load Criteria
// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.clear_criteria = function() {

	this.column_picker.clear();	
	this.column_picker.set_defaults();

	// clear filters
	// -------------
	for(var i=0; i<this.filter_fields.length; i++) {
		// reset filters
		this.filter_fields[i].df.filter_hide = 0;
		this.filter_fields[i].df.ignore = 0;
		if(this.filter_fields[i].is_custom) {
		
			// hide+ignore customized filters
			this.filter_fields[i].df.filter_hide = 1;
			this.filter_fields[i].df.ignore = 1;
		}
		
		this.filter_fields[i].set_input(null);
	}
	
	this.set_sort_options();
	
	this.set_main_title('Report: ' + get_doctype_label(this.doctype));

	this.current_loaded = null;
	this.customized_filters = null;
	this.sc = null;
	this.has_index = 1; this.has_headings = 1;

	for(var i in this.fn_list) this[this.fn_list[i]] = null; // clear custom functions
}

// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.set_main_title = function(title) {
	_r.rb_con.appframe.$titlebar.find('.report-title').html(title);
	set_title(title);
}

_r.ReportBuilder.prototype.select_column = function(dt, label, value) {
	if(value==null)value = 1;
	this.column_picker.set(dt, label, value);
}

// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.set_filter = function(dt, label, value) {
	if(this.filter_fields_dict[dt+'\1'+ label])
		this.filter_fields_dict[dt+'\1'+ label].set_input(value);
}

// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.load_criteria = function(criteria_name) {
	this.clear_criteria();
	
	if(!this.sc_dict[criteria_name]) {
		alert(criteria_name + ' could not be loaded. Please Refresh and try again');
	}
	this.sc = locals['Search Criteria'][this.sc_dict[criteria_name]];

	// eval the custom script
	var report = this;
	if(this.sc && this.sc.report_script) eval(this.sc.report_script);
	
	this.large_report = 0;

	// execute the customize_filters method from Search Criteria
	if(report.customize_filters) {
		try {
			report.customize_filters(this);
		} catch(err) {
			errprint('Error in "customize_filters":\n' + err);
		}
	}

	// refresh fiters
	this.report_filters.refresh();
	
	// set fields
	// ----------
	this.column_picker.clear();

	var cl = this.sc.columns ? this.sc.columns.split(',') : [];
	for(var c=0;c<cl.length;c++) {
		var key = cl[c].split('\1');
		this.select_column(key[0], key[1], 1);
	}

	// set filters
	// -----------
	eval('var fl=' + this.sc.filters);
	for(var n in fl) {
		if(fl[n]) {
			var key = n.split('\1');
			if(key[1]=='docstatus') { /* ? */ }
			this.set_filter(key[0], key[1], fl[n]);
		}
	}

	// refresh column picker
	this.set_criteria_sel(criteria_name);
	this.set_filters_from_route();
}

// -------------------------------------------------------------------------------------
// this method must be called after resetting the Search Criteria (or clearing)
// to set Data table properties

_r.ReportBuilder.prototype.set_criteria_sel = function(criteria_name) {

	// add additional columns
	var sc = locals['Search Criteria'][this.sc_dict[criteria_name]];
	if(sc && sc.add_col)
		var acl = sc.add_col.split('\n');
	else
		var acl = [];
	var new_sl = [];
	
	// update the label in datatable where the column name is specified in the query using AS
	for(var i=0; i<acl.length; i++) {
		var tmp = acl[i].split(' AS ');
		if(tmp[1]) {
			var t = eval(tmp[1]);
			new_sl[new_sl.length] = [t, "`"+t+"`"];
		}
	}
	
	// set sort
	this.set_sort_options(new_sl);
	if(sc && sc.sort_by) {
		this.dt.sort_sel.value = sc.sort_by;
	}
	if(sc && sc.sort_order) {
		sc.sort_order=='ASC' ? this.dt.set_asc() : this.dt.set_desc();
	}
	if(sc && sc.page_len) {
		this.dt.page_len_sel.inp.value = sc.page_len;
	}
	
	this.current_loaded = criteria_name;
	// load additional fields sort option
	this.set_main_title(criteria_name);
}

//
// Create the filter UI and column selection UI
// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.setup_filters_and_cols = function() {

	// function checks where there is submit permission on the DocType or if the DocType 
	// can be trashed
	function can_dt_be_submitted(dt) {
		return locals.DocType[dt] && locals.DocType[dt].is_submittable || 0;
	}

	var me = this;
	var dt = me.parent_dt?me.parent_dt:me.doctype;

	// default filters
	var fl = [
		{'fieldtype':'Data', 'label':'ID', 'fieldname':'name', 'in_filter':1, 'parent':dt},
		{'fieldtype':'Data', 'label':'Owner', 'fieldname':'owner', 'in_filter':1, 'parent':dt},
		{'fieldtype':'Date', 'label':'Created on', 'fieldname':'creation', 'in_filter':0, 'parent':dt},
		{'fieldtype':'Date', 'label':'Last modified on', 'fieldname':'modified', 'in_filter':0, 'parent':dt},
	];

	// can this be submitted?
	if(can_dt_be_submitted(dt)) {
		fl[fl.length] = {'fieldtype':'Check', 'label':'Saved', 'fieldname':'docstatus', 'search_index':1, 'in_filter':1, 'def_filter':1, 'parent':dt};
		fl[fl.length] = {'fieldtype':'Check', 'label':'Submitted', 'fieldname':'docstatus', 'search_index':1, 'in_filter':1, 'def_filter':1, 'parent':dt};
		fl[fl.length] = {'fieldtype':'Check', 'label':'Cancelled', 'fieldname':'docstatus', 'search_index':1, 'in_filter':1, 'parent':dt};
	}
	
	// make the datatable
	me.make_datatable();

	// Add columns and filters of parent doctype
	me.orig_sort_list = [];
	if(me.parent_dt) {
		me.setup_dt_filters_and_cols(fl, me.parent_dt); 
		var fl = [];
	}

	// Add columns and filters of selected doctype
	me.setup_dt_filters_and_cols(fl, me.doctype); 

	// hide primary filters blue box if there are no primary filters
	if(!this.has_primary_filters) 
		$dh(this.report_filters.first_page_filter);
	
	this.column_picker.refresh();
	
	// show body
	$ds(me.body);
}

_r.ReportBuilder.prototype.set_filters_from_route = function() {
	// add filters from route
	var route = wn.get_route();
	//save this for checking changes in filter
	this.current_route = wn.get_route_str();
	if(route.length>3) {
		for(var i=3; i<route.length; i++) {
			var p = route[i].split('=');
			if(p.length==2) {
				var dt = this.parent_dt ? this.parent_dt: this.doctype;
				this.set_filter(dt, p[0], p[1]);
			}
		} 
	}	
}

// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.add_filter = function(f) {
	if(this.filter_fields_dict[f.parent + '\1' + f.label]) {
		// exists
		this.filter_fields_dict[f.parent + '\1' + f.label].df = f; // reset properties
	} else {
		this.report_filters.add_field(f, f.parent, null, 1);
	}
}

// -------------------------------------------------------------------------------------
// this is where the filters and columns are created for a particular doctype

_r.ReportBuilder.prototype.setup_dt_filters_and_cols = function(fl, dt) {
	var me = this; 

	// set section headings
	var lab = $a(me.filter_area,'div','filter_dt_head');
	lab.innerHTML = 'Filters for ' + get_doctype_label(dt);

	var lab = $a(me.picker_area,'div','builder_dt_head');
	lab.innerHTML = 'Select columns for ' + get_doctype_label(dt);

	// get fields
	var dt_fields = wn.meta.docfield_list[dt];
	for(var i=0;i<dt_fields.length;i++) {
		fl[fl.length] = dt_fields[i];
	}
	
	// get "high priority" search fields
	// if the field is in search_field then it should be primary filter (i.e. on first page)
	
	var sf_list = locals.DocType[dt].search_fields ? locals.DocType[dt].search_fields.split(',') : [];
	for(var i in sf_list) sf_list[i] = strip(sf_list[i]);
	
	// make fields
	for(var i=0;i<fl.length;i++) {
	
		var f=fl[i];
		
		// add to filter
		if(f && cint(f.in_filter)) {
			me.report_filters.add_field(f, dt, in_list(sf_list, f.fieldname));
		}
		
		// add to column selector (builder) 
		if(f && !in_list(no_value_fields, f.fieldtype) && f.fieldname != 'docstatus' && (!f.report_hide)) {
			me.column_picker.add_field(f);
		}
	}

	me.set_sort_options();
}

// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.set_sort_options = function(l) {
	var sl = this.orig_sort_list;

	empty_select(this.dt.sort_sel);
		
	if(l) sl = add_lists(l, this.orig_sort_list);
	
	// make new list if reqd
	if(!l) l = [];
	
	// no sorts, add one
	if(!l.length) {
		l.push(['ID', 'name'])
	}
	
	for(var i=0; i<sl.length; i++) {
		this.dt.add_sort_option(sl[i][0], sl[i][1]);
	}
}

// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.validate_permissions = function(onload) {
	this.perm = get_perm(this.parent_dt ? this.parent_dt : this.doctype);
	if(!this.perm[0][READ]) {
		this.forbidden = 1;
		if(user=='Guest') {
			msgprint('You must log in to view this page');
		} else {
			msgprint('No Read Permission');
		}
		window.back();
		return 0;
	}
	return 1;
}

// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.setup_doctype = function(onload) {
	// load doctype
	var me = this;
	
	if(!locals['DocType'][this.doctype]) {
		this.load_doctype_from_server(onload);
	} else {
		// find parent dt if required
		for(var key in locals.DocField) {
			var f = locals.DocField[key];
			if(f.fieldtype=='Table' && f.options==this.doctype)
				this.parent_dt = f.parent;
		}
		if(!me.validate_permissions()) 
			return;
		me.validate_permissions();
		me.make_body();
		me.setup_filters_and_cols();
		if(onload)onload(me);
	}
}

_r.ReportBuilder.prototype.load_doctype_from_server = function(onload) {
	var me = this;
	$c('webnotes.widgets.form.load.getdoctype', args = {'doctype': this.doctype, 'with_parent':1 }, 
		function(r,rt) {
			if(r.parent_dt)me.parent_dt = r.parent_dt;
			if(!me.validate_permissions()) 
				return;
			me.make_body();
			me.setup_filters_and_cols();
			if(onload)onload(me);
		} 
	);
}
// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.reset_report = function() {
	this.clear_criteria();
	
	// show column picker if find
	this.mytabs.items['Select Columns'].show();
	this.mytabs.items['More Filters'].show();
  	
	this.report_filters.refresh();
	this.column_picker.refresh();
	
	var	dt = this.parent_dt?this.parent_dt: this.doctype;
	this.set_filter(dt, 'Saved', 1);
	this.set_filter(dt, 'Submitted', 1);
	this.set_filter(dt, 'Cancelled', 0);
	
	this.column_picker.set_defaults();

	this.dt.clear_all();
	
	this.dt.sort_sel.value = 'ID';
	this.dt.page_len_sel.inp.value = '50';
	this.dt.set_no_limit(0);
	this.dt.set_desc();
	
	this.set_filters_from_route();
}

//
// Make the SQL query
// -------------------------------------------------------------------------------------
 

_r.ReportBuilder.prototype.make_datatable = function() {
	var me = this;
	
	this.dt_area = $a(this.mytabs.items['Result'].body, 'div');

	var clear_area = $a(this.mytabs.items['Result'].body, 'div');
	clear_area.style.marginTop = '8px';
	clear_area.style.textAlign = 'right';
	
	this.clear_btn = $a($a(clear_area, 'span'), 'button');
	this.clear_btn.innerHTML = 'Clear Settings';
	this.clear_btn.onclick = function() {
		me.reset_report();
	}

	var d = $a(clear_area, 'span', '', {marginLeft:'16px'});
	d.innerHTML = '<span>Show Query: </span>';
	this.show_query = $a_input(d, 'checkbox');
	this.show_query.checked = false;

	
	this.dt = new _r.DataTable(this.dt_area, '');
	this.dt.finder = this;
	this.dt.make_query = function() {
		// attach report script functions
		var report = me;
		
		// get search criteria
		if(me.current_loaded && me.sc_dict[me.current_loaded]) {
			var sc = get_local('Search Criteria', me.sc_dict[me.current_loaded]);
		}
		
		if(sc) me.dt.search_criteria = sc;
		else me.dt.search_criteria = null;

		// reset no_limit
		//me.dt.set_no_limit(0);

		//load server script
		if(sc && sc.server_script) me.dt.server_script = sc.server_script;
		else me.dt.server_script = null;
	
		// load client scripts - attach all functions from ReportBuilder to Datatable
		// this is a bad way of doing things but since DataTable is a stable object
		// currently this is okay.... to change in future

		for(var i=0;i<me.fn_list.length;i++) {
			if(me[me.fn_list[i]]) me.dt[me.fn_list[i]] = me[me.fn_list[i]];
			else me.dt[me.fn_list[i]] = null;
		}
		
		var fl = []; // field list
		var docstatus_cl = [];
		var cl = []; // cond list
		
		// format table name
		var table_name = function(t) { return '`tab' + t + '`'; }

		// advanced - make list of diabled filters
		var dis_filters_list = [];
		if(sc && sc.dis_filters)
			var dis_filters_list = sc.dis_filters.split('\n');
		
		// make a list of selected columns from ColumnPicker in tableName.fieldName format
		var t = me.column_picker.get_selected();
		for(var i=0;i<t.length;i++) {
			fl.push(table_name(t[i].parent) + '.`'+t[i].fieldname+'` AS `'+t[i].parent +'.'+ t[i].fieldname+'`');
		}
		me.selected_fields = fl;
				
		// advanced - additional fields
		if(sc && sc.add_col) {
			var adv_fl = sc.add_col.split('\n');
			for(var i=0;i<adv_fl.length;i++) {
				fl[fl.length] = adv_fl[i];
			}
		}

		// build dictionary for filter values for server side
		me.dt.filter_vals = {} 
		add_to_filter = function(k,v,is_select) {
			if(v==null)v='';
			if(!in_list(keys(me.dt.filter_vals), k)) {
				me.dt.filter_vals[k] = v;
			} else {
				if(is_select)
					me.dt.filter_vals[k] += '\n' + v;
				else
					me.dt.filter_vals[k+'1'] = v; // for date, numeric (from-to)
			}
		}

		// loop over the fields and construct the SQL query
		// ------------------------------------------------
		for(var i=0;i<me.filter_fields.length;i++) {
			var t = me.filter_fields[i];
			
			// add to "filter_values"
			var v = t.get_value?t.get_value():'';
			if(t.df.fieldtype=='Select') {
				if(t.input.multiple) {
					for(var sel_i=0;sel_i < v.length; sel_i++) {
						add_to_filter(t.df.fieldname, v[sel_i], 1);
					}
					// no values? atleast add key
					if(!v.length) add_to_filter(t.df.fieldname, "", 1);
				} else {
					add_to_filter(t.df.fieldname, v);
				}
			} else add_to_filter(t.df.fieldname, v);
			
			// if filter is not disabled
			if(!in_list(dis_filters_list, t.df.fieldname) && !t.df.ignore) {
				if(t.df.fieldname=='docstatus') {
	
					// work around for docstatus
					// -------------------------
					
					if(t.df.label=='Saved'){
						if(t.get_value()) docstatus_cl[docstatus_cl.length] = table_name(t.df.parent)+'.docstatus=0';
						else cl[cl.length] = table_name(t.df.parent)+'.docstatus!=0';
					}
					else if(t.df.label=='Submitted'){
						if(t.get_value()) docstatus_cl[docstatus_cl.length] = table_name(t.df.parent)+'.docstatus=1';
						else cl[cl.length] = table_name(t.df.parent)+'.docstatus!=1';
					}
					else if(t.df.label=='Cancelled'){
						if(t.get_value()) docstatus_cl[docstatus_cl.length] = table_name(t.df.parent)+'.docstatus=2';
						else cl[cl.length] = table_name(t.df.parent)+'.docstatus!=2';
					}
				} else { 
					
					// normal
					// -------
					var fn = '`' + t.df.fieldname + '`';
					var v = t.get_value?t.get_value():'';
					if(v) {
						if(in_list(['Data','Link','Small Text','Text'],t.df.fieldtype)) {
							cl[cl.length] = table_name(t.df.parent) + '.' + fn + ' LIKE "' + v + '%"';

						} else if(t.df.fieldtype=='Select') {
							if(t.input.multiple) {
								// loop for multiple select
								var tmp_cl = [];
								for(var sel_i=0;sel_i < v.length; sel_i++) {
									if(v[sel_i]) {
										tmp_cl[tmp_cl.length] = table_name(t.df.parent) + '.' + fn + ' = "' + v[sel_i] + '"';
									}
								}
								
								// join multiple select conditions by OR
								if(tmp_cl.length)cl[cl.length] = '(' + tmp_cl.join(' OR ') + ')';
							} else {
								cl[cl.length] = table_name(t.df.parent) + '.' + fn + ' = "' + v + '"';
							}
						} else {
							var condition = '=';
							if(t.sql_condition) condition = t.sql_condition;
							cl[cl.length] = table_name(t.df.parent) + '.' + fn + condition + '"' + v + '"';
						}
					}
				}
			}
		}
		
		// standard filters
		me.dt.filter_vals.user = user;
		me.dt.filter_vals.user_email = user_email;
		me.filter_vals = me.dt.filter_vals; // in both dt and report

		// overloaded query - finish it here
		this.is_simple = 0;
		if(sc && sc.custom_query) {
			this.query = repl(sc.custom_query, me.dt.filter_vals);
			this.is_simple = 1;
			return
		}
		
		if(me.get_query) {
			// custom query method
			this.query = me.get_query();
			this.is_simple = 1;
		} else {
			// add docstatus conditions
			if(docstatus_cl.length)
				cl[cl.length] = '('+docstatus_cl.join(' OR ')+')';
	
			// advanced - additional conditions
			if(sc && sc.add_cond) {
				var adv_cl = sc.add_cond.split('\n');
				for(var i=0;i< adv_cl.length;i++) {
					cl[cl.length] = adv_cl[i];
				}
			}
	
			// atleast one field
			if(!fl.length) {
				alert('You must select atleast one column to view');
				this.query = '';
				return;
			}
	
			// join with parent in case of child
			var tn = table_name(me.doctype);
			if(me.parent_dt) {
				tn = tn + ',' + table_name(me.parent_dt);
				cl[cl.length] = table_name(me.doctype) + '.`parent` = ' + table_name(me.parent_dt) + '.`name`';
			}
			
			// advanced - additional tables
			if(sc && sc.add_tab) {
				var adv_tl = sc.add_tab.split('\n');
				tn = tn + ',' + adv_tl.join(',');
			}
			
			// make the query
			if(!cl.length)
				this.query = 'SELECT ' + fl.join(',\n') + ' FROM ' + tn
			else
				this.query = 'SELECT ' + fl.join(',') + ' FROM ' + tn + ' WHERE ' + cl.join('\n AND ');
	
			// advanced - group by
			if(sc && sc.group_by) {
				this.query += ' GROUP BY ' + sc.group_by;
			}
	
			// replace - in custom query if %(key)s is specified, then replace it by filter values
			this.query = repl(this.query, me.dt.filter_vals)
		}
		
		if(me.show_query.checked) {
			this.show_query = 1;
		}
		
		// report name - used as filename in export
		if(me.current_loaded) this.rep_name = me.current_loaded;
		else this.rep_name = me.doctype;
	}
}

// -------------------------------------------------------------------------------------

_r.ReportBuilder.prototype.get_filter = function(dt, label) {
	return this.filter_fields_dict[dt + FILTER_SEP + label];
}

_r.ReportBuilder.prototype.set_filter_properties = function(dt, label, properties) {
	var f = this.filter_fields_dict[dt + FILTER_SEP + label];
	for(key in properties) {
		f.df[key]=properties[key];
	}
}

// Report Filter
// ===================================================================================

_r.ReportFilters = function(rb) {
	this.rb = rb;

	// filters broken into - primary - in searchfields and others
	this.first_page_filter = $a(rb.mytabs.items['Result'].body, 'div', 'finder_filter_area');
	this.filter_area = $a(rb.mytabs.items['More Filters'].body, 'div', 'finder_filter_area');
	
	// filter fields area
	this.filter_fields_area = $a(this.filter_area,'div');

}

// -------------------------------------------------------------------------------------

_r.ReportFilters.prototype.refresh = function() {
	// called after customization
	var fl = this.rb.filter_fields
	
	for(var i=0; i<fl.length; i++) {
		var f = fl[i];
		
		// is hidden ?
		if(f.df.filter_hide) { 
			$dh(f.wrapper); 
		} else {
			$ds(f.wrapper);
		}
		
		// is bold?
		if(f.df.bold) { 
			if(f.label_cell) 
				$y(f.label_cell, {fontWeight:'bold'}) 
		} else { 
			if(f.label_cell) $y(f.label_cell, {fontWeight:'normal'}) 
		}
		
		// set default value
		if(f.df['report_default']) 
			f.set_input(f.df['report_default']);
			
		// show in first page?
		if(f.df.in_first_page && f.df.filter_cell) {
			f.df.filter_cell.parentNode.removeChild(f.df.filter_cell);
			this.first_page_filter.appendChild(f.df.filter_cell);
			this.rb.has_primary_filters = 1;
			$ds(this.first_page_filter);
		}
		
		// clear / hide all custom added filters
	}
}

// -------------------------------------------------------------------------------------

_r.ReportFilters.prototype.add_date_field = function(cell, f, dt, is_custom) {
	var my_div = $a(cell,'div','',{});
	
	// from date
	var f1 = copy_dict(f);
	f1.label = 'From ' + f1.label;
	var tmp1 = this.make_field_obj(f1, dt, my_div, is_custom);
	tmp1.sql_condition = '>=';
	tmp1.bound = 'lower';

	// to date
	var f2 = copy_dict(f);
	f2.label = 'To ' + f2.label;
	var tmp2 = this.make_field_obj(f2, dt, my_div, is_custom);
	tmp2.sql_condition = '<=';
	tmp2.bound = 'upper';
}

// -------------------------------------------------------------------------------------

_r.ReportFilters.prototype.add_numeric_field = function(cell, f, dt, is_custom) {
	var my_div = $a(cell,'div','',{});
	
	// from value
	var f1 = copy_dict(f);
	f1.label = f1.label + ' >=';
	var tmp1 = this.make_field_obj(f1, dt, my_div, is_custom);
	tmp1.sql_condition = '>=';
	tmp1.bound = 'lower';

	// to value
	var f2 = copy_dict(f);
	f2.label = f2.label + ' <=';
	var tmp2 = this.make_field_obj(f2, dt, my_div, is_custom);
	tmp2.sql_condition = '<=';
	tmp2.bound = 'upper';		
}

// make a field object
_r.ReportFilters.prototype.make_field_obj = function(f, dt, parent, is_custom) {
	var tmp = make_field(f, dt, parent, this.rb, false);
	tmp.not_in_form = 1;
	tmp.in_filter = 1;
	tmp.refresh();
	this.rb.filter_fields[this.rb.filter_fields.length] = tmp;
	this.rb.filter_fields_dict[f.parent + '\1' + f.label] = tmp;
	if(is_custom) tmp.is_custom = 1;
	return tmp;	
}

// -------------------------------------------------------------------------------------

_r.ReportFilters.prototype.add_field = function(f, dt, in_primary, is_custom) {
	var me = this;
		
	// insert in (parent element)
	if(f.in_first_page) in_primary = true;
	
	var fparent = this.filter_fields_area;
	if(in_primary) { 
		fparent = this.first_page_filter; 
		this.rb.has_primary_filters = 1; 
	}
	
	// label
	// --- ability to insert
	if(f.on_top) {
		var cell = document.createElement('div');
		fparent.insertBefore(cell, fparent.firstChild);
		$y(cell,{width:'70%'});

	} else if(f.insert_before) {
		var cell = document.createElement('div');
		fparent.insertBefore(cell, fparent[f.df.insert_before].filter_cell);
		$y(cell,{width:'70%'});		
	}

	else
		var cell = $a(fparent, 'div', '', {width:'70%'});

	f.filter_cell = cell;
		
	// make field
	if(f.fieldtype=='Date') {
		// date field
		this.add_date_field(cell, f, dt);
	} else if(in_list(['Currency', 'Int', 'Float'], f.fieldtype)) {
		// numeric
		this.add_numeric_field(cell, f, dt);
	} else if (!in_list(['Section Break', 'Column Break', 'Read Only', 'HTML', 'Table', 'Image', 'Button'], f.fieldtype)) {
		var tmp = this.make_field_obj(f, dt, cell, is_custom);
	}
	
	// add to datatable sort
	if(f.fieldname != 'docstatus')
		me.rb.orig_sort_list.push([f.label, '`tab' + f.parent + '`.`' + f.fieldname + '`']);
			
	// check saved
	if(f.def_filter)
		tmp.input.checked = true;
}



// Column Picker
// ===================================================================================

_r.ReportColumnPicker = function(rb) {
	this.rb = rb;
	this.picker_area = $a(this.rb.mytabs.items['Select Columns'].body, 'div', 'finder_picker_area');
	
	this.all_fields = [];
	this.sel_idx = 0;
	
	this.make_body();
}

// -------------------------------------------------------------------------------------

_r.ReportColumnPicker.prototype.make_body = function() {

	var t = make_table(this.picker_area, 1, 3, '100%', ['35%','30%','35%'], {verticalAlign:'middle', textAlign:'center'});

	// all fields
	$a($td(t,0,0), 'h3', '', {marginBottom:'8px'}).innerHTML = 'Columns';
	this.unsel_fields = $a($td(t,0,0), 'select', '', {height:'200px', width:'100%', border:'1px solid #AAA'});
	this.unsel_fields.multiple = true;
	this.unsel_fields.onchange = function() { for(var i=0; i<this.options.length; i++) this.options[i].field.is_selected = this.options[i].selected; }

	// buttons
	var me = this;
	this.up_btn = $a($a($td(t,0,1), 'div'), 'button', '', {width:'70px'});
	this.up_btn.innerHTML = 'Up &uarr;';
	this.up_btn.onclick = function() { me.move_up(); }

	this.add_all = $a($a($td(t,0,1), 'div'), 'button', '', {width:'40px'});
	this.add_all.innerHTML = '&gt;&gt;';
	this.add_all.onclick = function() { me.move(me.unsel_fields, 'add', 1); }

	this.add_btn = $a($a($td(t,0,1), 'div'), 'button', '', {width:'110px'});
	this.add_btn.innerHTML = '<b>Add &gt;</b>';
	this.add_btn.onclick = function() { me.move(me.unsel_fields, 'add'); }
		
	this.remove_btn = $a($a($td(t,0,1), 'div'), 'button', '', {width:'110px'});
	this.remove_btn.innerHTML = '<b>&lt; Remove</b>';
	this.remove_btn.onclick = function() { me.move(me.sel_fields, 'remove'); }

	this.remove_all = $a($a($td(t,0,1), 'div'), 'button', '', {width:'40px'});
	this.remove_all.innerHTML = '&lt;&lt;';
	this.remove_all.onclick = function() { me.move(me.sel_fields, 'remove', 1); }

	this.dn_btn = $a($a($td(t,0,1), 'div'), 'button', '', {width:'70px'});
	this.dn_btn.innerHTML = 'Down &darr;';
	this.dn_btn.onclick = function() { me.move_down(); }

	// multiple fields
	$a($td(t,0,2), 'h3', '', {marginBottom:'8px'}).innerHTML = 'Selected Columns';
	this.sel_fields = $a($td(t,0,2), 'select', '', {height:'200px', width:'100%', border:'1px solid #AAA'});
	this.sel_fields.multiple = true;
	this.sel_fields.onchange = function() { for(var i=0; i<this.options.length; i++) this.options[i].field.is_selected = this.options[i].selected; }

}



// -------------------------------------------------------------------------------------

_r.ReportColumnPicker.prototype.get_by_sel_idx = function(s, idx) {
	for(var j=0;j<s.options.length; j++) {
		if(s.options[j].field.sel_idx == idx)
			return s.options[j].field;
	}
	return {} // nothing
}

_r.ReportColumnPicker.prototype.move_up = function() {
	var s = this.sel_fields;
	for(var i=1;i<s.options.length; i++ ) {
		if(s.options[i].selected) {
			s.options[i].field.sel_idx--;
			this.get_by_sel_idx(s, i-1).sel_idx++;
		}
	}
	this.refresh();
}

_r.ReportColumnPicker.prototype.move_down = function() {
	var s = this.sel_fields;
	
	if(s.options.length<=1) return;
	
	for(var i=s.options.length-2;i>=0; i-- ) {
		if(s.options[i].selected) {
			this.get_by_sel_idx(s, i+1).sel_idx--;
			s.options[i].field.sel_idx++;
		}
	}
	this.refresh();
}



// -------------------------------------------------------------------------------------

_r.ReportColumnPicker.prototype.move = function(s, type, all) {
	for(var i=0;i<s.options.length; i++ ) {
		if(s.options[i].selected || all) {
			if(type=='add') {
				s.options[i].field.selected = 1;
				s.options[i].field.sel_idx = this.sel_idx;
				this.sel_idx++;
			} else {
				s.options[i].field.selected = 0;
				s.options[i].field.sel_idx = 0;
				this.sel_idx--;
			}
		}
	}
	this.refresh();
}

// -------------------------------------------------------------------------------------

_r.ReportColumnPicker.prototype.refresh = function() {
	// separate
	var ul = []; var sl=[];
	for(var i=0; i<this.all_fields.length; i++) {
		var o = this.all_fields[i];
		if(o.selected) {
			sl.push(o);
			// enable sort option
			if(this.rb.dt) this.rb.dt.set_sort_option_disabled(o.df.label, 0);
		} else {
			ul.push(o);
			// disable sort option
			if(this.rb.dt) this.rb.dt.set_sort_option_disabled(o.df.label, 1);
		}
	}

	
	// sort by field idx
	ul.sort(function(a,b){return (cint(a.df.idx)-cint(b.df.idx))});
	
	// sort by order in which they were selected
	sl.sort(function(a,b){return (cint(a.sel_idx)-cint(b.sel_idx))})

	// re-number selected
	for(var i=0; i<sl.length; i++) { sl[i].sel_idx = i; }
	
	// add options
	this.set_options(this.unsel_fields, ul);
	this.set_options(this.sel_fields, sl);

}

// -------------------------------------------------------------------------------------

_r.ReportColumnPicker.prototype.set_options = function(s, l) {
	empty_select(s);

	for(var i=0; i<l.length; i++) {
		var v = l[i].df.parent + '.' + l[i].df.label;
		var v_label = get_doctype_label(l[i].df.parent) + '.' + l[i].df.label;		
		var o = new Option (v_label, v, false, false);
		o.field = l[i];
		if(o.field.is_selected) o.selected = 1;
		s.options[s.options.length] = o;
	}
}

// -------------------------------------------------------------------------------------

_r.ReportColumnPicker.prototype.clear = function() {
	this.sel_idx = 0;
	for(var i=0; i<this.all_fields.length; i++) {
		this.all_fields[i].selected = 0;	
	}
	this.refresh();
}

// -------------------------------------------------------------------------------------

_r.ReportColumnPicker.prototype.get_selected = function() {
	var sl = [];
	for(var i=0; i<this.all_fields.length; i++) {
		var o = this.all_fields[i];
		if(o.selected) {
			sl[sl.length] = o.df;
			o.df.sel_idx = o.sel_idx;
		}
	}
	return sl.sort(function(a,b){return (cint(a.sel_idx)-cint(b.sel_idx))});
}

// -------------------------------------------------------------------------------------

_r.ReportColumnPicker.prototype.set_defaults = function() {
	for(var i=0; i<this.all_fields.length; i++) {
		if(this.all_fields[i].selected_by_default)
			this.all_fields[i].selected = 1;
	}
}

// -------------------------------------------------------------------------------------

_r.ReportColumnPicker.prototype.add_field = function(f) {
	// column picker
	if(!f.label) return;
	
	var by_default = (f.in_filter) ? 1 : 0;
	
	this.all_fields.push({
		selected:by_default
		,df:f
		,sel_idx: (by_default ? this.sel_idx : 0)
		,selected_by_default : by_default
	});

	this.sel_idx += by_default;

}

// -------------------------------------------------------------------------------------

_r.ReportColumnPicker.prototype.set = function(dt, label, selected) {
	for(var i=0; i<this.all_fields.length; i++) {
		if(this.all_fields[i].df.parent == dt && this.all_fields[i].df.label==label) {
			this.all_fields[i].selected = selected;
			this.all_fields[i].sel_idx = this.sel_idx;
			this.sel_idx += cint(selected);
			this.refresh();
			return;
		}
	}
}


/*
 *	lib/js/legacy/widgets/report_builder/datatable.js
 */
// Copyright (c) 2012 Web Notes Technologies Pvt Ltd (http://erpnext.com)
// 
// MIT License (MIT)
// 
// Permission is hereby granted, free of charge, to any person obtaining a 
// copy of this software and associated documentation files (the "Software"), 
// to deal in the Software without restriction, including without limitation 
// the rights to use, copy, modify, merge, publish, distribute, sublicense, 
// and/or sell copies of the Software, and to permit persons to whom the 
// Software is furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in 
// all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
// PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
// CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
// OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
// 

/// Data Table


_r.scroll_head = function(ele) {
	var h = ele.childNodes[0];
	h.style.top = cint(ele.scrollTop) + 'px';
}

_r.DataTable = function(html_fieldname, dt, repname, hide_toolbar) {
	
	
  var me = this;
  if(html_fieldname.substr) {
	  var html_field = cur_frm.fields_dict[html_fieldname];
  
	  // override onrefresh
	  html_field.onrefresh = function() {
	  	if(me.docname != cur_frm.docname) {
	  	  me.clear_all();
	  	  me.docname = cur_frm.docname;
	  	}
	  }
  
	  var parent = html_field.wrapper;
	  datatables[html_fieldname] = this;
  } else {
  	var parent = html_fieldname;
  }

  this.start_rec = 1;
  this.page_len = 50;
  this.repname = repname;
  this.dt = dt;
  this.no_limit = false;
  this.query = '';
  this.has_index = 1;
  this.has_headings = 1;  //this.sort_options = {};
  this.disabled_options = {};
  
  this.levels = [];
  
  // make ui

  // new link
  if(this.dt) {
    var tw = $a(parent, 'div');
  	var t = $a(tw, 'div', 'link_type');
  	t.style.cssFloat = 'right';
  	$h(tw, '14px');
  	t.style.margin = '2px 0px';
  	t.style.fontSize = '11px';
  	t.onclick = function() { new_doc(me.dt); }
  	t.innerHTML = 'New '+ this.dt;
  }

  // toolbar
  if(!hide_toolbar) this.make_toolbar(parent);

  this.wrapper = $a(parent, 'div', 'report_tab');
  $h(this.wrapper, cint(screen.height * 0.35) + 'px');

  this.wrapper.onscroll = function() {_r.scroll_head(this); }
  
  this.hwrapper = $a(this.wrapper, 'div', 'report_head_wrapper');
  this.twrapper = $a(this.wrapper, 'div', 'report_tab_wrapper');
  
  this.no_data_tag = $a(this.wrapper, 'div', 'report_no_data');
  this.no_data_tag.innerHTML = 'No Records Found';

  this.fetching_tag = $a(this.wrapper, 'div', '', {height:'100%', background:'url("images/lib/ui/square_loading.gif") center no-repeat', display:'none'});  
}

_r.DataTable.prototype.add_icon = function(parent, imgsrc) {
  var i = $a(parent, 'img');
  i.style.padding = '2px';
  i.style.cursor = 'pointer';
  i.setAttribute('src', 'images/lib/icons/'+imgsrc+'.gif');
  return i;
}

_r.DataTable.prototype.set_no_limit = function(v) {
	if(v) {
		this.no_limit = 1;
		$dh(this.page_len_sel.wrapper);
	} else {
		this.no_limit = 0;
		$ds(this.page_len_sel.wrapper);		
	}
}

_r.DataTable.prototype.make_toolbar = function(parent) {
  var me = this;
  
  // headbar
  this.hbar = $a(parent, 'div', '', {margin:'8px 0px 16px 0px'});

  var ht = make_table(this.hbar,1,3,'100%',['40%','40%','20%'],{verticalAlign:'middle'});
  var div = $a($td(ht,0,0), 'div');
  
  // sort select
  var t = make_table($td(ht,0,1),1,6,null,[null,null,null,'20px',null,null],{verticalAlign:'middle'});

  $td(t,0,0).innerHTML = 'Sort By:'; $y($td(t,0,1),{textAlign:'right',paddingRight:'4px'});
  
  this.sort_sel = $a($td(t,0,2), 'select','',{width:'100px'});

  this.sort_sel.onchange = function() {
    me.start_rec = 1;
    me.run();
  }

  // sort order
  this.sort_icon = this.add_icon($td(t,0,3), 'arrow_down');
  this.sort_order = 'DESC';
  
  this.sort_icon.onclick = function() {
  	if(me.sort_order=='ASC') me.set_desc();
    else me.set_asc();

    me.start_rec = 1;
    me.run();
  }

  // page len

  $td(t,0,4).innerHTML = 'Per Page:'; $y($td(t,0,4),{textAlign:'right',paddingRight:'4px'});  
  var s = new SelectWidget($td(t,0,5), ['50','100','500','1000'], '70px');
  s.inp.value = '50';

  s.inp.onchange = function() { 
  	me.page_len = flt(this.value);
  }
  this.page_len_sel = s;

  var c1 = $td(ht,0,2);
  c1.style.textAlign = 'right';

  // first page
  var ic = this.add_icon(c1, 'resultset_first');
  ic.onclick = function() {
  	me.start_rec = 1;
  	me.run();
  }
  
  // prev page
  var ic = this.add_icon(c1, 'resultset_previous');
  ic.onclick = function() {
    if(me.start_rec - me.page_len <= 0)return;
  	me.start_rec = me.start_rec - me.page_len;
  	me.run();
  }
  
  // next page
  this.has_next = false;
  var ic = this.add_icon(c1, 'resultset_next');
  ic.onclick = function() {
    if(!me.has_next)return;
  	me.start_rec = me.start_rec + me.page_len;
  	me.run();
  }

}

_r.DataTable.prototype.set_desc = function() {
	this.sort_icon.src = 'images/lib/icons/arrow_down.gif'; this.sort_order='DESC';
}
_r.DataTable.prototype.set_asc = function(icon) {
	this.sort_icon.src = 'images/lib/icons/arrow_up.gif'; this.sort_order='ASC'; 
}

////

_r.DataTable.prototype.set_sort_option_disabled = function(label, disabled) {
  // has bugs due to sequencing
  // may not set during load
	
  var s = this.sort_sel;
  if(disabled) {
  	// remove this option
    for(var i=0; i<s.options.length; i++) {
      if(s.options[i] && s.options[i].text==label) {
        this.disabled_options[label] = s.options[i];
        s.remove(i);
      }
    }
  } else {
  	// get it back
    if(this.disabled_options[label]) {
      try {
        s.add(this.disabled_options[label], s.options[s.options.length-1]);
      } catch(e) {
      	try {
      	  s.add(this.disabled_options[label], s.options.length-1);
      	} catch (e) { }
      }
      this.disabled_options[label] = null;
    }
  }
  
  
}

_r.DataTable.prototype.add_sort_option = function(label, val) {
  var s = this.sort_sel;
  s.options[s.options.length] = 
         new Option(label, val, false, s.options.length==0?true:false);
}


_r.DataTable.prototype.update_query = function(no_limit) { 

  // add sorting
  if((_r.rb_con.cur_rb && _r.rb_con.cur_rb.get_query) || (this.search_criteria && this.search_criteria.custom_query)) {
  	// no sorting if custom_query or get_query
  } else {
	if(!sel_val(this.sort_sel)) {
		this.sort_sel.selectedIndex = 0; // select the first value (IE)
	}
	this.query += NEWLINE 
             + ' ORDER BY ' + sel_val(this.sort_sel)
             + ' ' + this.sort_order;
  }
  
  if(no_limit || this.no_limit) {
    if(this.show_query) alert(this.query);
  	return;
  }
  
  // add paging  
  this.query += ' LIMIT ' + (this.start_rec-1) + ',' + this.page_len;
  if(this.show_query)
	alert(this.query);

}

_r.DataTable.prototype._get_query = function(no_limit) {
	$dh(this.no_data_tag);
	this.show_query = 0;
  	if(this.make_query)
  		this.make_query();
	this.update_query(no_limit);
}

_r.DataTable.prototype.run = function() {
  if(this.validate && !this.validate())
    return;

  if(_r.rb_con.cur_rb) {
  	if(_r.rb_con.cur_rb.large_report == 1) {
  	  msgprint("This is a very large report and cannot be shown in the browser as it is likely to make your browser very slow.<br><br>Please click on 'Export' to open in a spreadsheet");
  	  return;
  	}
  	_r.rb_con.cur_rb.mytabs.items['Result'].expand();
  }
  
  var me = this;
  this._get_query();
  
  // preset data
  if(this.set_data) {
  	this.show_result(this.set_data);
  	this.set_data = null;
  	return;
  }
    
  $ds(this.fetching_tag);
  if($.browser.mozilla)this.clear_all();
  
  var args = { 
			'query':me.query,
			'report_name': '_r.DataTable', 
			'show_deleted':1,
			'sc_id':me.search_criteria ? me.search_criteria.name : '',
			'filter_values':me.filter_vals ? docstring(me.filter_vals) : '',
			'roles':'["'+user_roles.join('","')+'"]'
		}

  if(this.is_simple) args.is_simple = 1;

  $c('webnotes.widgets.query_builder.runquery', args, function(r,rt) {  
  	$dh(me.fetching_tag); 
  	me.show_result(r,rt); 
  });
  
}

_r.DataTable.prototype.clear_all = function() {
	// clear old
	if(this.htab && this.htab.parentNode) {
		this.htab.parentNode.removeChild(this.htab); delete this.htab; }
	if(this.tab && this.tab.parentNode) {
		this.tab.parentNode.removeChild(this.tab); delete this.tab; }
	$dh(this.no_data_tag);

}

_r.DataTable.prototype.has_data = function() {
	if(this.htab && this.htab.rows.length)return 1;
	else return 0;
}

_r.DataTable.prototype.show_result = function(r, rt) {
	// clear old
	var me = this;
	this.clear_all();

	this.rset = eval(r.values);

	if(this.rset && this.rset.length) {

		// add 
		if(this.has_headings) {
			this.htab = $a(this.hwrapper, 'table');
			$y(this.twrapper,{top:'25px',borderTop:'0px'});
		}
		this.tab = $a(this.twrapper, 'table');
	
		this.colwidths  = eval(r.colwidths);
		this.coltypes   = eval(r.coltypes);
		this.coloptions = eval(r.coloptions);
		this.colnames = eval(r.colnames);
	
		$y(this.tab,{tableLayout:'fixed'});
	
		if(this.beforetableprint)this.beforetableprint(this);

		// heading
		if(this.has_headings) this.make_head_tab(this.colnames);
	
		// data
	 	var start = this.start_rec;
	 	
		// show max 1000
	 	var rset_len = this.rset.length;
	 	if(rset_len > 1000) {
	 		msgprint("Showing only 1000 records out of " + rset_len + ". Use 'Export' to see all records");
	 		rset_len = 1000;
	 	}
	  
		for(var vi=0; vi<rset_len; vi++) {
			var row = this.tab.insertRow(vi);
			// for script

			if(this.has_index) {
				var c0 = row.insertCell(0);
				$w(c0, '30px');
				$a(c0, 'div', '', {width:'23px'}).innerHTML = start;
			}
	      
			// cells
			start++;      
			for(var ci=0;ci < this.rset[vi].length;ci++) {
				this.make_data_cell(vi, ci, this.rset[vi][ci]);
			}
		  
			if(this.afterrowprint) {
				row.data_cells = {}; row.data = {};
				for(var ci=0;ci< this.colnames.length;ci++) {
					row.data[this.colnames[ci]] = this.rset[vi][ci];
					row.data_cells[this.colnames[ci]] = row.cells[ci+1];
				}f
				this.afterrowprint(row);
			}
  
		}

		// has next page?
		if(this.rset.length && this.rset.length>=this.page_len)this.has_next = true;
	
		// style
		if(r.style) {
			for(var i=0;i<r.style.length;i++) {
				$yt(this.tab,r.style[i][0],r.style[i][1],r.style[i][2]);
			}
		}	
	
		// after table print
		if(this.aftertableprint) this.aftertableprint(this.tab);


	} else {
		$ds(this.no_data_tag);
	}
}

_r.DataTable.prototype.get_col_width = function(i) {
	if(this.colwidths 
		&& this.colwidths.length 
			&& this.colwidths[i])
				return cint(this.colwidths[i]) +'px';
	else return '100px';
}

_r.DataTable.prototype.make_head_tab = function(colnames) {
	var r0 = this.htab.insertRow(0);
	if(this.has_index) {
		var c0 = r0.insertCell(0);
		c0.className = 'report_head_cell';
		$w(c0, '30px');
		$a(c0, 'div').innerHTML = 'Sr';
		this.total_width = 30;  
	}
	
	for(var i=0;i<colnames.length;i++) {
		var w = this.get_col_width(i);
		this.total_width+=cint(w);  
	
		var c = r0.insertCell(r0.cells.length);
		c.className = 'report_head_cell';
		if(w)$w(c, w);
		$a(c,'div').innerHTML = colnames[i];
		c.val = colnames[i];
	}
	$w(this.htab, this.total_width + 'px');
	$w(this.tab, this.total_width + 'px');
}

_r.DataTable.prototype.make_data_cell = function(ri, ci, val) {
  var row = this.tab.rows[ri];
  var c = row.insertCell(row.cells.length);
  
  // row style:
  if(row.style.color) 
  	c.style.color = row.style.color;
  if(row.style.backgroundColor) 
  	c.style.backgroundColor = row.style.backgroundColor;
  if(row.style.fontWeight) 
  	c.style.fontWeight = row.style.fontWeight;
  if(row.style.fontSize) 
  	c.style.fontSize = row.style.fontSize;
  
  var w = this.get_col_width(ci);
  if(w)$w(c, w);
  c.val = val;
  
  var me = this;

  c.div = $a(c, 'div', '', {width:(cint(w)-7)+'px'});
  $s(c.div, val, this.coltypes[ci], this.coloptions[ci])
}

_r.DataTable.prototype.do_print = function() {
	this._get_query(true);  
	
	args = {
		query : this.query,
		title : this.rep_name?this.rep_name:this.dt,
		colnames : null,
		colwidhts : null,
		coltypes : null, 
		has_index : this.has_index, 
		has_headings: this.has_headings,
		check_limit : 1,
		is_simple : (this.is_simple ? 'Yes' : ''),
		sc_id : (this.search_criteria ? this.search_criteria.name : ''),
		filter_values : docstring(this.filter_vals),
		//finder: this.finder ? this.finder : null
	};
	
	wn.require('js/print_query.js');	
	_p.print_query = new _p.PrintQuery();
	_p.print_query.show_dialog(args);
}

_r.DataTable.prototype.do_export = function() {
	this._get_query(true);

	var me = this;
	export_query(this.query, function(q) {
		export_csv(q, (me.rep_name?me.rep_name:me.dt), (me.search_criteria?me.search_criteria.name:''), me.is_simple, docstring(me.filter_vals));	
	});
}

// Calculator 
// ----------
_r.DataTable.prototype.do_calc = function() {
	_r.show_calc(this.tab, this.colnames, this.coltypes, 1);
}

_r.DataTable.prototype.get_col_data = function(colname) {
	var ci = 0;
	if(!this.htab) return [];
    for(var i=1;i<this.htab.rows[0].cells.length;i++) {
		var hc = this.htab.rows[0].cells[i];
    	if(hc.val == colname) {
    		ci = i;
    		break;
    	}
    }
	
	var ret = [];
	for(var ri=0;ri<this.tab.rows.length;ri++) {
		ret[ret.length] = this.tab.rows[ri].cells[ci].val;
	}
	return ret;
}

_r.DataTable.prototype.get_html = function() {
	var w = document.createElement('div');
	w = $a(w, 'div');
	w.style.marginTop = '16px';
	var tab = $a(w, 'table');

	var add_head_style = function(c, w) {
		c.style.fontWeight = 'bold';
		c.style.border = '1px solid #000';
		c.style.padding = '2px';
		if(w)$w(c, w);
		return c;
	}

	var add_cell_style = function(c) {
		c.style.padding = '2px';
		c.style.border = '1px solid #000';
		return c;
	}

	tab.style.borderCollapse = 'collapse';  
	var hr = tab.insertRow(0);
	var c0 = add_head_style(hr.insertCell(0), '30px');
	c0.innerHTML = 'Sr';
  
	// heading
	for(var i=1;i<this.htab.rows[0].cells.length;i++) {
		var hc = this.htab.rows[0].cells[i];
		var c = add_head_style(hr.insertCell(i), hc.style.width);
		c.innerHTML = hc.innerHTML;
	}
  
	// data
	for(var ri=0;ri<this.tab.rows.length;ri++) {
		var row = this.tab.rows[ri];
		var dt_row = tab.insertRow(tab.rows.length);
		for(var ci=0;ci<row.cells.length;ci++) {
			var c = add_cell_style(dt_row.insertCell(ci));
			c.innerHTML = row.cells[ci].innerHTML;
		}
	}
	return w.innerHTML;
}



/*
 *	lib/js/legacy/widgets/report_builder/calculator.js
 */
// Copyright (c) 2012 Web Notes Technologies Pvt Ltd (http://erpnext.com)
// 
// MIT License (MIT)
// 
// Permission is hereby granted, free of charge, to any person obtaining a 
// copy of this software and associated documentation files (the "Software"), 
// to deal in the Software without restriction, including without limitation 
// the rights to use, copy, modify, merge, publish, distribute, sublicense, 
// and/or sell copies of the Software, and to permit persons to whom the 
// Software is furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in 
// all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
// PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
// CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
// OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
// 

// Calculator 
// ----------
_r.calc_dialog = null;
_r.show_calc = function(tab, colnames, coltypes, add_idx) {
	if(!add_idx) add_idx = 0;
	if(!tab || !tab.rows.length) { msgprint("No Data"); return; }
	
	if(!_r.calc_dialog) {
		var d = new Dialog(400,400,"Calculator")
		d.make_body([
			['Select','Column']
			,['Data','Sum']
			,['Data','Average']
			,['Data','Min']
			,['Data','Max']
		])
		d.widgets['Sum'].readonly = 'readonly';
		d.widgets['Average'].readonly = 'readonly';
		d.widgets['Min'].readonly = 'readonly';
		d.widgets['Max'].readonly = 'readonly';
		d.widgets['Column'].onchange = function() {
			d.set_calc();
		}
		d.set_calc = function() {
			// get the current column of the data table
			var cn = sel_val(this.widgets['Column']);
			var cidx = 0; var sum=0; var avg=0; var minv = null; var maxv = null;
			for(var i=0;i<this.colnames.length;i++) {if(this.colnames[i]==cn){ cidx=i+add_idx; break; } }
			for(var i=0; i<this.datatab.rows.length; i++) {
				var c = this.datatab.rows[i].cells[cidx];
				var v = c.div ? flt(c.div.innerHTML) : flt(c.innerHTML);
				sum += v;
				if(minv == null) minv = v;
				if(maxv == null) maxv = v;
				if(v > maxv)maxv = v;
				if(v < minv)minv = v;
			}
			d.widgets['Sum'].value = fmt_money(sum);
			d.widgets['Average'].value = fmt_money(sum / this.datatab.rows.length);
			d.widgets['Min'].value = fmt_money(minv);
			d.widgets['Max'].value = fmt_money(maxv);
			_r.calc_dialog = d;
		}
		d.onshow = function() {
			// set columns
			var cl = []; 
			for(var i in _r.calc_dialog.colnames) {
				if(in_list(['Currency','Int','Float'],_r.calc_dialog.coltypes[i])) 
					cl.push(_r.calc_dialog.colnames[i]);
			}
			if(!cl.length) {
				this.hide();
				alert("No Numeric Column");
				return;
			}
			var s = this.widgets['Column'];
			empty_select(s);
			add_sel_options(s, cl);
			if(s.inp)s.inp.value = cl[0];
			else s.value = cl[0];
			this.set_calc();
		}
		_r.calc_dialog = d;
	}
	_r.calc_dialog.datatab = tab;
	_r.calc_dialog.colnames = colnames;
	_r.calc_dialog.coltypes = coltypes;
	_r.calc_dialog.show();
}

