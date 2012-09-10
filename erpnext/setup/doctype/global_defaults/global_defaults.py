# ERPNext - web based ERP (http://erpnext.com)
# Copyright (C) 2012 Web Notes Technologies Pvt Ltd
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Global Defaults"""
import webnotes
from webnotes.model.controller import DocListController

keydict = {
	"fiscal_year": "current_fiscal_year",
    'company': 'default_company',
    'currency': 'default_currency',
    'price_list_name': 'default_price_list',
	'price_list_currency': 'default_price_list_currency',
    'item_group': 'default_item_group',
    'customer_group': 'default_customer_group',
    'cust_master_name': 'cust_master_name', 
    'supplier_type': 'default_supplier_type',
    'supp_master_name': 'supp_master_name', 
    'territory': 'default_territory',
    'stock_uom': 'default_stock_uom',
    'fraction_currency': 'default_currency_fraction',
    'valuation_method': 'default_valuation_method',
	'date_format': 'date_format',
	'currency_format':'default_currency_format',
	'account_url':'account_url',
	'allow_negative_stock' : 'allow_negative_stock',
	'maintain_same_rate' : 'maintain_same_rate'
}

class GlobalDefaultsController(DocListController):
	def on_update(self):
		for key in keydict:
			webnotes.conn.set_default(key, self.doc.get(keydict[key], ''))
			
		# update year start date and year end date from fiscal_year
		ysd, yed = webnotes.conn.get_value('Fiscal Year', self.doc.current_fiscal_year, \
			['year_start_date', 'year_end_date'])
			
		from webnotes.utils import get_first_day, get_last_day
		if ysd:
			webnotes.conn.set_default('year_start_date', ysd.strftime('%Y-%m-%d'))
		if yed:
			webnotes.conn.set_default('year_end_date', yed.strftime('%Y-%m-%d'))
		
	def get_defaults(self):
		return webnotes.conn.get_defaults()
