from odoo import models, fields

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    #product_qty is how many to buy, desired_qty is how many have been requested through procurements.
    #They differ only when seller.round_up is applied
    desired_qty = fields.Float(string='Quantity needed by underlying procurements', digits='Product Unit of Measure', default=0.0)