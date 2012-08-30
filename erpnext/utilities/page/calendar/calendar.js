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

wn.pages.calendar.on('load', function(wrapper) {
	wn.ui.make_app_page({
		parent: wrapper,
		single_column: true,
		title: 'Calendar'
	});
	
	wn.require('js/lib/fullcalendar/fullcalendar.css');
	wn.require('js/lib/jquery/jquery.ui.interactions.min.js');
	wn.require('js/lib/fullcalendar/fullcalendar.js');
	
	$('<div id="fullcalendar">').appendTo($(wrapper).find('.layout-main')).fullCalendar({
		header: {
			left: 'prev,next today',
			center: 'title',
			right: 'month,agendaWeek,agendaDay'
		},
		editable: true,
		events: function(start, end, callback) {
			wn.call({
				method: 'utilities.page.calendar.calendar.get_events',
				args: {
					start: start,
					end: end
				},
				callback: function(r) {
					callback(r.message);
				}
			})
		},
		dayClick: function(date, allDay, jsEvent, view) {
			// if current date, show popup to create a new event
			var ev = wn.model.create('Event')
			ev.doc.set('start', date);
			ev.doc.set('end', new Date(date));
			ev.doc.set('all_day', 1);
			
			if(!(date.getHours()==0 && date.getMinutes()==0)) {
				// default event one hour
				ev.doc.get('end').setHours(date.getHours() + 1);
				ev.doc.set('all_day', 0);
			}
			console.log(ev.doc.get('end'))
			
			$('#fullcalendar').fullCalendar('renderEvent', {
				start: ev.doc.get('start'),
				end: ev.doc.get('end'),
				title: ev.doc.get('name'),
				allDay: ev.doc.get('all_day') ? true : false
			})
		},
		eventClick: function(calEvent, jsEvent, view) {
			// edit event description or delete
		}
	});
});