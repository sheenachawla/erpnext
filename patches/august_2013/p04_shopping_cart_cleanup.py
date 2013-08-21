# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd.
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes

def execute():
	import webnotes.defaults
	webnotes.defaults.clear_default("shopping_cart_quotation_series", parent="Control Panel")