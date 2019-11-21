from odoo import models, fields

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _update_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, line):
        #temporarily set product_qty back to desired_qty, so we ignore this MOQ for the purposes of running the parent logic
        if line.desired_qty:  #in case it's not set.  This will also be the case if desired_qty = 0, which seems ok?
            #We assume there is no case where desired_qty = 0 could lead to product_qty != 0
            #So we're safe to leave product_qty unchanged if desired_qty = 0
            #The other case is that we've inherited a PO where desired_qty didn't exist, in which case we definitely want to start with product_qty as-is
            line.product_qty = line.desired_qty

        res = super()._update_purchase_order_line(product_id, product_qty, product_uom, company_id, values, line)

        #Re-find the seller
        seller = product_id.with_context(force_company=company_id.id)._select_seller(
            partner_id=values['supplier'].name,
            quantity=res['product_qty'],
            date=line.order_id.date_order and line.order_id.date_order.date(),
            uom_id=product_id.uom_po_id)

        #What the module calculated as product_qty is really desired_qty; product_qty is after applying MOQ & increment
        res['desired_qty'] = res['product_qty']
        if seller:
            res['product_qty'] = seller.round_to_moq(res['desired_qty'])
        return res

    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, po):
        res = super()._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, values, po)

        #Re-find the seller
        seller = product_id.with_context(force_company=company_id.id)._select_seller(
            partner_id=values['supplier'].name,
            quantity=res['product_qty'],
            date=po.date_order and po.date_order.date(),
            uom_id=product_id.uom_po_id)

        #What the module calculated as product_qty is really desired_qty; product_qty is after applying MOQ & increment
        res['desired_qty'] = res['product_qty']
        if seller:
            res['product_qty'] = seller.round_to_moq(res['desired_qty'])
        return res