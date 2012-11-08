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

// list of communications
// start new communication

erpnext.MailBox = Class.extend({
	init: function(opts) {
		$.extend(this, opts);
		this.make();
	},
	make: function() {
		var me = this;
		this.listing = new wn.ui.Listing({
			parent: this.parent,
			method: "utilities.doctype.communication.communication.get_communication",
			render_row: function(parent, value, listing, row_idx) {
				value._modified = dateutil.comment_when(value.modified);
				if(!value.status) value.status = "Open";
				value._from = value.from ? "("+value.from+")" : "";
				
				$(parent).html(repl("<span class='label'>%(status)s</span> \
					%(subject)s %(_from)s\
					<span class='pull-right'>%(_modified)s</span>", value))
					.css({"cursor": "pointer"})
					.attr("data-row", row_idx)
					.click(function() {
						new erpnext.ThreadView(me.listing.data[$(this).attr("data-row")]);
					});
			}
		});
		this.listing.run();
	}
});

erpnext.ThreadView = Class.extend({
	init: function(opts) {
		$.extend(this, opts);
		this.make();
	},
	make: function() {
		this.dialog = new wn.ui.Dialog({
			title: this.subject,
			width: 640,
		})
		this.listing = new wn.ui.Listing({
			parent: this.dialog.body,
			method: "utilities.doctype.communication.communication.get_communication",
			args: {
				thread: this.name
			}
		})
		this.dialog.show();
		this.listing.run();
	}
})