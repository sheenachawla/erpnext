import webnotes

def get_unread_messages(session):
	"returns unread (docstatus-0 messages for a user)"
	return session.db.sql("""\
		SELECT name, comment
		FROM `tabComment`
		WHERE parenttype IN ('My Company', 'Message')
		AND parent = %s
		AND ifnull(docstatus,0)=0
		""", session.user, as_list=1)

def get_open_support_tickets(session):
	"""Returns a count of open support tickets"""
	from webnotes.utils import cint
	open_support_tickets = session.db.sql("""\
		SELECT COUNT(*) FROM `tabSupport Ticket`
		WHERE status = 'Open'""", as_list=1)
	return open_support_tickets and cint(open_support_tickets[0][0]) or 0

def get_open_tasks(session):
	"""Returns a count of open tasks"""
	from webnotes.utils import cint
	return session.db.sql("""\
		SELECT COUNT(*) FROM `tabTask`
		WHERE status = 'Open'""", as_list=1)[0][0]

def get_things_todo(session):
	"""Returns a count of incomplete todos"""
	from webnotes.utils import cint
	incomplete_todos = session.db.sql("""\
		SELECT COUNT(*) FROM `tabToDo`
		WHERE IFNULL(checked, 0) = 0
		AND owner = %s""", session.user, as_list=1)
	return incomplete_todos and cint(incomplete_todos[0][0]) or 0

def get_todays_events(session):
	"""Returns a count of todays events in calendar"""
	from webnotes.utils import nowdate, cint
	todays_events = session.db.sql("""\
		SELECT COUNT(*) FROM `tabEvent`
		WHERE owner = %s
		AND event_type != 'Cancel'
		AND event_date = %s""", (
		session.user, nowdate(session)), as_list=1)
	return todays_events and cint(todays_events[0][0]) or 0

def get_unanswered_questions(session):
	return len(filter(lambda d: d[0]==0,
		session.db.sql("""select (select count(*) from tabAnswer 
		where tabAnswer.question = tabQuestion.name) as answers from tabQuestion""", as_list=1)))
	
@webnotes.whitelist()
def get_global_status_messages(session):
	return {
		'unread_messages': get_unread_messages(session),
		'open_support_tickets': get_open_support_tickets(session),
		'things_todo': get_things_todo(session),
		'todays_events': get_todays_events(session),
		'open_tasks': get_open_tasks(session),
		'unanswered_questions': get_unanswered_questions(session)
	}
