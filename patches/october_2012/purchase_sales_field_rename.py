def execute():
	remove_fields()
	rename_fields()
	
	# TODO
	# calculate 
	# taxes_and_charges_print
	# missing rounded totals and missing rounded total imports
	# missing amounts in words

def remove_fields():
	pass

def rename_fields():
	pass
	
rename_map = {
	"Purchase Taxes and Charges": [
		["purchase_tax_details", "taxes_and_charges"],
	],
	"Sales Taxes and Charges": [
		["cost_center_other_charges", "cost_center"],
	],
	"Sales Taxes and Charges Master": [
		["other_charges", "taxes_and_charges"],
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
		["purchase_other_charges", "purchase_taxes_and_charges"],
		["total_tax", "taxes_and_charges_total"],
		["grand_total_import", "grant_total_print"],
		["net_total_import", "net_total_print"],
		["conversion_rate", "exchange_rate"],
		["in_words", "grand_total_in_words"],
		["in_words_import", "grand_total_in_words_print"],
	],
	"Supplier Quotation Item": [
		["import_ref_rate", "ref_rate_print"],
		["discount_rate", "discount"],
		["import_rate", "rate_print"],
		["import_amount", "amount_print"],
		["purchase_ref_rate", "ref_rate"],
		["purchase_rate", "rate"],
		["prevdoc_docname", "purchase_request"],
		["prevdoc_date", "purchase_request_date"],
		["prevdoc_detail_docname", "purchase_request_item"],
	],
	"Purchase Order": [
		["transaction_date", "posting_date"],
		["po_details", "purchase_order_items"],
		["net_total_import", "net_total_print"],
		["conversion_rate", "exchange_rate"],
		["indent_no", "purchase_request"],
		["purchase_other_charges", "purchase_taxes_and_charges"],
		["purchase_tax_details", "taxes_and_charges"],
		["total_tax", "taxes_and_charges_total"],
		["in_words", "grand_total_in_words"],
		["grand_total_import", "grant_total_print"],
		["in_words_import", "grand_total_in_words_print"],
	],
	"Purchase Order Item": [
		["import_ref_rate", "ref_rate_print"],
		["discount_rate", "discount"],
		["import_rate", "rate_print"],
		["import_amount", "amount_print"],
		["purchase_ref_rate", "ref_rate"],
		["purchase_rate", "rate"],
		["prevdoc_docname", "purchase_request"],
		["prevdoc_date", "purchase_request_date"],
		["prevdoc_detail_docname", "purchase_request_item"],
	],
	"Purchase Invoice": [
	
	]
}
	
remove_map = {
	"Purchase Taxes and Charges": ["add_deduct_tax", "total_tax_amount",
		"total_amount"],
	"Sales Taxes and Charges": ["total_tax_amount", "total_amount"],
	"Supplier Quotation": ["other_charges_added", "other_charges_deducted"],
	"Supplier Quotation Item": ["prevdoc_doctype"],
	"Purchase Order": ["other_charges_added", "other_charges_deducted", "ref_sq"],
	"Purchase Order Item": ["prevdoc_doctype"],
	
}