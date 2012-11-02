import webnotes

def execute():
	# first sync so that new columns get created!
	webnotes.conn.commit()
	from webnotes.model.sync import sync_all
	sync_all()
	webnotes.conn.begin()
	
	rename_fields()
	rename_prevdoc_fields()
	remove_fields()
	delete_docs()
	
	# TODO
	# calculate 
	# taxes_and_charges_print
	# missing rounded totals and missing rounded total imports
	# missing amounts in words
	# TODO: sales cycle patch! prevdoc_docname, prevdoc_doctype split for lead and opportunity
	# TODO: sales cycle patch! ref_rate --> print_ref_rate then base_ref_rate --> ref_rate

def rename_fields():
	print "Rename Fields"
	from webnotes.model.doctype import rename_field
	
	for dt, fields_list in sorted(rename_map.items()):
		print dt
		for fields_pair in sorted(fields_list, reverse=True):
			print fields_pair
			rename_field(dt, fields_pair[0], fields_pair[1], lookup_field=fields_pair[1])
		print
		
def rename_prevdoc_fields():
	print "Rename prevdoc fields"
	from webnotes.modules import scrub
	for dt, dt_pairs in prevdoc_rename_map.items():
		print dt
		columns = [c[0] for c in webnotes.conn.sql("""desc `tab%s`""" % dt)]
		if "prevdoc_doctype" in columns:
			for parent, item in dt_pairs:
				webnotes.conn.sql("""update `tab%s` set `%s`=`prevdoc_docname`
					where prevdoc_doctype=%s""" % (dt, scrub(parent), "%s"),
					(parent,))
				if "prevdoc_detail_docname" in columns:
					webnotes.conn.sql("""update `tab%s` set `%s`=`prevdoc_detail_docname`
						where prevdoc_doctype=%s""" % (dt, scrub(item), "%s"),
						(parent,))
			print "Updated [case 1]: ", dt_pairs
		elif "prevdoc_docname" in columns and len(dt_pairs)==1:
			webnotes.conn.sql("""update `tab%s` set `%s`=`prevdoc_docname`""" % \
				(dt, scrub(dt_pairs[0][0])))
			if "prevdoc_detail_docname" in columns:
				webnotes.conn.sql("""update `tab%s` set `%s`=`prevdoc_detail_docname`""" \
					% (dt, scrub(dt_pairs[0][1])))
			print "Updated [case 2]: ", dt_pairs
		else:
			print "Not Updated: ", dt_pairs
	print

def remove_fields():
	print "Removing Fields"
	webnotes.conn.commit()
	
	tables = [t[0] for t in webnotes.conn.sql("""show tables""")];
	
	for dt, fields_list in rename_map.items():
		if dt not in remove_map:
			remove_map[dt] = []

		for fields_pair in fields_list:
			if fields_pair[0] not in remove_map[dt]:
				remove_map[dt].append(fields_pair[0])
				
	for dt in prevdoc_rename_map:
		if dt not in remove_map:
			remove_map[dt] = []
		
		for f in ["prevdoc_doctype", "prevdoc_docname", "prevdoc_date",
				"prevdoc_detail_docname"]:
			if f not in remove_map[dt]:
				remove_map[dt].append(f)
	
	for dt, fields_list in remove_map.items():
		if ("tab%s" % dt) in tables:
			columns = [c[0] for c in webnotes.conn.sql("""desc `tab%s`""" % dt)]
			drop_query = ", ".join(["drop column `%s`" % f
				for f in fields_list if f in columns])
			query = """alter table `tab%s` %s""" % (dt, drop_query)
			print query
			print
			webnotes.conn.sql(query)
	
	webnotes.conn.begin()
	
def delete_docs():
	print "Deleting Docs"
	import webnotes.model
	for dt, docs in delete_map.items():
		if docs == "All":
			docs = [d[0] for d in webnotes.conn.sql("select name from `tab%s`" % dt)]
		for d in docs:
			print "delete_doc(%s, %s)" % (dt, d)
			webnotes.model.delete_doc(dt, d)
	
rename_map = {
	"Purchase Taxes and Charges Master": [
		["purchase_tax_details", "taxes_and_charges"],
	],
	"Sales Taxes and Charges Master": [
		["cost_center_other_charges", "cost_center"],
	],
	"Purchase Request": [
		["transaction_date", "posting_date"],
		["indent_details", "purchase_request_items"],
		["sales_order_no", "sales_order"],
	],
	"Purchase Request Item": [
		["sales_order_no", "sales_order"],
	],
	"Supplier Quotation": [
		["transaction_date", "posting_date"],
		["quotation_items", "supplier_quotation_items"],
		["indent_no", "purchase_request"],
		["purchase_tax_details", "taxes_and_charges"],
		["purchase_other_charges", "taxes_and_charges_master"],
		["total_tax", "taxes_and_charges_total"],
		["grand_total_import", "grand_total_print"],
		["net_total_import", "net_total_print"],
		["conversion_rate", "exchange_rate"],
		["in_words", "grand_total_in_words"],
		["in_words_import", "grand_total_in_words_print"],
	],
	"Supplier Quotation Item": [
		["import_ref_rate", "print_ref_rate"],
		["discount_rate", "discount"],
		["import_rate", "print_rate"],
		["import_amount", "print_amount"],
		["purchase_ref_rate", "ref_rate"],
		["purchase_rate", "rate"],
	],
	"Purchase Order": [
		["transaction_date", "posting_date"],
		["po_details", "purchase_order_items"],
		["net_total_import", "net_total_print"],
		["conversion_rate", "exchange_rate"],
		["indent_no", "purchase_request"],
		["purchase_other_charges", "taxes_and_charges_master"],
		["purchase_tax_details", "taxes_and_charges"],
		["total_tax", "taxes_and_charges_total"],
		["grand_total_import", "grand_total_print"],
		["in_words", "grand_total_in_words"],
		["in_words_import", "grand_total_in_words_print"],
	],
	"Purchase Order Item": [
		["import_ref_rate", "print_ref_rate"],
		["discount_rate", "discount"],
		["import_rate", "print_rate"],
		["import_amount", "print_amount"],
		["purchase_ref_rate", "ref_rate"],
		["purchase_rate", "rate"],
	],
	"Purchase Invoice": [
		["entries", "purchase_invoice_items"],
		["net_total_import", "net_total_print"],
		["conversion_rate", "exchange_rate"],
		["purchase_order_main", "purchase_order"],
		["purchase_receipt_main", "purchase_receipt"],
		["purchase_other_charges", "taxes_and_charges_master"],
		["purchase_tax_details", "taxes_and_charges"],
		["total_tax", "taxes_and_charges_total"],
		["grand_total_import", "grand_total_print"],
		["in_words", "grand_total_in_words"],
		["in_words_import", "grand_total_in_words_print"],
	],
	"Purchase Invoice Item": [
		["import_ref_rate", "print_ref_rate"],
		["discount_rate", "discount"],
		["import_rate", "print_rate"],
		["import_amount", "print_amount"],
		["purchase_ref_rate", "ref_rate"],
		["po_detail", "purchase_order_item"],
		["pr_detail", "purchase_receipt_item"],
	],
	"Purchase Receipt": [
		["purchase_receipt_details", "purchase_receipt_items"],
		["purchase_order_no", "purchase_order"],
		["pull_purchase_order_details", "pull_purchase_order_items"], # button
		["net_total_import", "net_total_print"],
		["conversion_rate", "exchange_rate"],
		["purchase_other_charges", "taxes_and_charges_master"],
		["purchase_tax_details", "taxes_and_charges"],
		["total_tax", "taxes_and_charges_total"],
		["grand_total_import", "grand_total_print"],
		["in_words", "grand_total_in_words"],
		["in_words_import", "grand_total_in_words_print"],
	],
	"Purchase Receipt Item": [
		["import_ref_rate", "print_ref_rate"],
		["discount_rate", "discount"],
		["import_rate", "print_rate"],
		["import_amount", "print_amount"],
		["purchase_ref_rate", "ref_rate"],
		["purchase_rate", "rate"],
		["project_name", "project"],
		["qa_no", "quality_inspection"],
	],	
	"Opportunity": [
		["enquiry_details", "opportunity_items"],
		["transaction_date", "posting_date"],
	],
	"Quotation": [
		["transaction_date", "posting_date"],
		["quotation_details", "quotation_items"],
		["enq_no", "opportunity"],
		["plc_conversion_rate", "plc_exchange_rate"],
		["conversion_rate", "exchange_rate"],
		["charge", "taxes_and_charges_master"],
		["other_charges", "taxes_and_charges"],
		["other_charges_total", "taxes_and_charges_total"],
		["other_charges_calculation", "tax_calculation"],
		["grand_total_export", "grand_total_print"],
		["rounded_total_export", "rounded_total_print"],
		["in_words", "rounded_total_in_words"],
		["in_words_export", "rounded_total_in_words_print"],
	],
	"Quotation Item": [
		["ref_rate", "print_ref_rate"],
		["adj_rate", "discount"],
		["export_rate", "print_rate"],
		["export_amount", "print_amount"],
		["base_ref_rate", "ref_rate"],
		["basic_rate", "rate"],
	],
	"Sales Order": [
		["transaction_date", "posting_date"],
		["sales_order_details", "sales_order_items"],
		["quotation_no", "quotation"],
		["plc_conversion_rate", "plc_exchange_rate"],
		["conversion_rate", "exchange_rate"],
		["charge", "taxes_and_charges_master"],
		["other_charges", "taxes_and_charges"],
		["other_charges_total", "taxes_and_charges_total"],
		["other_charges_calculation", "tax_calculation"],
		["grand_total_export", "grand_total_print"],
		["rounded_total_export", "rounded_total_print"],
		["packing_details", "delivery_note_packing_items"],
		["in_words", "rounded_total_in_words"],
		["in_words_export", "rounded_total_in_words_print"],
	],
	"Sales Order Item": [
		["ref_rate", "print_ref_rate"],
		["adj_rate", "discount"],
		["export_rate", "print_rate"],
		["export_amount", "print_amount"],
		["base_ref_rate", "ref_rate"],
		["basic_rate", "rate"],
		["reserved_warehouse", "warehouse"],
	],
	"Sales Invoice": [
		["entries", "sales_invoice_items"],
		["sales_order_main", "sales_order"],
		["delivery_note_main", "delivery_note"],
		["plc_conversion_rate", "plc_exchange_rate"],
		["conversion_rate", "exchange_rate"],
		["charge", "taxes_and_charges_master"],
		["other_charges", "taxes_and_charges"],
		["other_charges_total", "taxes_and_charges_total"],
		["other_charges_calculation", "tax_calculation"],
		["grand_total_export", "grand_total_print"],
		["rounded_total_export", "rounded_total_print"],
		["packing_details", "delivery_note_packing_items"],
		["in_words_export", "rounded_total_in_words_print"],
		["in_words", "rounded_total_in_words"],
	],
	"Sales Invoice Item": [
		["ref_rate", "print_ref_rate"],
		["adj_rate", "discount"],
		["export_rate", "print_rate"],
		["export_amount", "print_amount"],
		["base_ref_rate", "ref_rate"],
		["basic_rate", "rate"],
		["so_detail", "sales_order_item"],
		["dn_detail", "delivery_note_item"],
	],
	"Delivery Note": [
		["delivery_note_details", "delivery_note_items"],
		["sales_order_no", "sales_order"],
		["plc_conversion_rate", "plc_exchange_rate"],
		["conversion_rate", "exchange_rate"],
		["charge", "taxes_and_charges_master"],
		["other_charges", "taxes_and_charges"],
		["other_charges_total", "taxes_and_charges_total"],
		["other_charges_calculation", "tax_calculation"],
		["grand_total_export", "grand_total_print"],
		["rounded_total_export", "rounded_total_print"],
		["packing_details", "delivery_note_packing_items"],
		["in_words_export", "rounded_total_in_words_print"],
		["in_words", "rounded_total_in_words"],
	],
	"Delivery Note Item": [
		["ref_rate", "print_ref_rate"],
		["adj_rate", "discount"],
		["export_rate", "print_rate"],
		["export_amount", "print_amount"],
		["base_ref_rate", "ref_rate"],
		["basic_rate", "rate"],
		# TODO: add options in prevdocs
	],
	"Packing Slip": [
		["item_details", "packing_slip_items"],
	],
	"Sales Taxes and Charges Master": [
		["other_charges", "taxes_and_charges"],
	],
	"Maintenance Schedule": [
		["transaction_date", "posting_date"],
		["sales_order_no", "sales_order"],
	],
	"Maintenance Visit": [
		["sales_order_no", "sales_order"],
		["customer_issue_no", "customer_issue"],
	]
}
	
remove_map = {
	"Purchase Taxes and Charges": ["add_deduct_tax", "total_tax_amount",
		"total_amount"],
	"Sales Taxes and Charges": ["total_tax_amount", "total_amount"],
	"Supplier Quotation": ["other_charges_added", "other_charges_deducted",
		"other_charges_added_import", "other_charges_deducted_import"],
	"Supplier Quotation Item": ["prevdoc_doctype"],
	"Purchase Order": ["other_charges_added", "other_charges_deducted",
		"other_charges_added_import", "other_charges_deducted_import"],
	"Purchase Order Item": ["prevdoc_doctype"],
	"Purchase Invoice": ["other_charges_added", "other_charges_deducted",
		"other_charges_added_import", "other_charges_deducted_import"],
	"Purchase Receipt": ["other_charges_added", "other_charges_deducted",
		"other_charges_added_import", "other_charges_deducted_import"],
	"Opportunity Item": ["basic_rate"],
	"Quotation Item": ["prevdoc_doctype", "prevdoc_name"],
	"Sales Order Item": ["transaction_date"],
	"Sales Invoice Item": ["clear_pending"],
	"Delivery Note Item": ["prevdoc_doctype", "prevdoc_docname", "prevdoc_date", 
		"prevdoc_detail_docname"],
	"Delivery Note Packing Item": ["prevdoc_doctype"],
}

delete_map = {
	"GL Mapper": "All",
	"Search Criteria": ["monthly_transaction_summary", "yearly_transaction_summary",
		"variance_report", ],
	"Print Format": ["Form 16A Print Format"],
}

prevdoc_rename = ["Supplier Quotation Item", "Purchase Order Item", "Purchase Receipt Item", ]

prevdoc_rename_map = {
	"Supplier Quotation Item": [
		["Purchase Request", "Purchase Request Item"],
	],
	"Purchase Order Item": [
		["Purchase Request", "Purchase Request Item"],
		["Supplier Quotation", "Supplier Quotation Item"],
	],
	"Purchase Receipt Item": [
		["Purchase Order", "Purchase Order Item"],
	],
	"Quotation Item": [
		["Opportunity", "Opportunity Item"],
	],
	"Sales Order Item": [
		["Quotation", "Quotation Item"],
	],
	"Delivery Note Item": [
		["Sales Order", "Sales Order Item"],
		["Sales Invoice", "Sales Invoice Item"],
	]
	
}