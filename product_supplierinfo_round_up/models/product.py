# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = "product.product"
    def _select_seller(self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False):
        res = super()._select_seller(partner_id, quantity, date, uom_id, params)
        if not res:
            #do another round looking for a match taking into account seller.round_up
            return res
        return res

class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    increment_qty = fields.Float(
        'Order Increment', default=0.0,
        help="The increment in which the part must be ordered, expressed in the vendor Product Unit of Measure if not any, in the default unit of measure of the product otherwise.")
    round_up = fields.Boolean('Round to MOQ', default=False, help="If ticked, RFQ quantities will be adjusted to match MOQ and order increment.")  

    def round_to_moq(self, desired_qty):
        if self.round_up:
            #TODO take into account min_qty and increment_qty
            #remember, increment quantity isn't required
            to_order_qty = desired_qty
        else:
            to_order_qty = desired_qty
        return to_order_qty
