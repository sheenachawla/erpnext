// render
wn.doclistviews['Party'] = wn.views.ListView.extend({
	init: function(d) {
		this._super(d)
		this.fields = this.fields.concat([
			"`tabParty`.party_type",
			"`tabParty`.party_group",
			"`tabCustomer`.territory",
		]);
		this.show_hide_check_column();
	},
	
	prepare_data: function(data) {
		this._super(data);
		//data.name = repl("<a href=\"#!Form/Customer/%(name)s\">%(name)s</a>", data);
	},
	
	columns: [
		{width: '5%', content:'check'},
		{width: '5%', content:'avatar'},
		//{width: '20%', content:'name'},
		{width: '15%', content:'party_type'},
		{width: '15%', content:'party_group'},
		{width: '10%', content:'tags'},
		{width: '15%', content:'territory', css: {'color': '#aaa'}},
		{width: '15%', content:'modified', css: {'text-align': 'right', 'color':'#777'}}
	],
});
