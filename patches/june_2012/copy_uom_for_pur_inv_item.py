from __future__ import unicode_literals
def execute():
	import webnotes
	
	# perform sync
	import webnotes.model.sync
	webnotes.model.sync.sync('buying', 'purchase_order_item')
	webnotes.model.sync.sync('accounts', 'purchase_invoice_item')
	webnotes.model.sync.sync('stock', 'purchase_receipt_item')
	
	webnotes.conn.sql("update `tabPurchase Invoice Item` t1, `tabPurchase Order Item` t2 set t1.uom = t2.uom where ifnull(t1.purchase_order_item, '') != '' and t1.purchase_order_item = t2.name")
	webnotes.conn.sql("update `tabPurchase Invoice Item` t1, `tabPurchase Receipt Item` t2 set t1.uom = t2.uom where ifnull(t1.purchase_receipt_item, '') != '' and t1.purchase_receipt_item = t2.name")