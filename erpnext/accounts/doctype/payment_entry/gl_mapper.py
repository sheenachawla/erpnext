gl_mapper = [
	{
		'account'				: 'receivable_payable_account',
		'party'					: 'party',
		'posting_date'			: 'posting_date',
		'debit'					: "eval:self.doc.send_or_receive == 'Send' \
			and self.doc.payment_amount or None",
		'credit'				: "eval:self.doc.send_or_receive == 'Receive' \
			and self.doc.payment_amount or None",		
		'voucher_type'			: 'doctype',
		'voucher_no'			: 'name',
		'company'				: 'company',
		'remarks'				: 'remarks',
		'against_voucher_type'	: "eval:(self.doc.sales_invoice and 'val:Sales Invoice') \
			or (self.doc.purchase_invoice and 'val:Purchase Invoice') or None",
		'against_voucher'		: "eval:self.doc.sales_invoice or self.doc.purchase_invoice and self.doc.name or None"
		
	},
	{
		'account'				: 'bank_cash_account',
		'posting_date'			: 'posting_date',
		'debit'					: "eval:self.doc.send_or_receive == 'Receive' \
			and self.doc.payment_amount or None",
 		'credit'				: "eval:self.doc.send_or_receive == 'Send' \
			and self.doc.payment_amount or None",
		'voucher_type'			: 'doctype',
		'voucher_no'			: 'name',
		'company'				: 'company',
		'remarks'				: 'remarks'
	}
	
]