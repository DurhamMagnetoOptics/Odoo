# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools import float_compare

class ProductProduct(models.Model):
    _inherit = "product.product"
    def _select_seller(self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False):
        res = super()._select_seller(partner_id, quantity, date, uom_id, params)
        if not res:
            #Nothing was found whwere we meet the MOQ
            # so do another round looking for a match taking into account seller.round_up
            res = self.select_roundup_seller(partner_id, date, params)
        return res

    def select_roundup_seller(self, partner_id, date, params):
        self.ensure_one()
        if date is None:
            date = fields.Date.context_today(self)

        res = self.env['product.supplierinfo']
        sellers = self._prepare_sellers(params)

        #Only look at supplierinfo where we've said it's ok to round up to the MOQ
        sellers = sellers.filtered(lambda s: s.round_up)

        if self.env.context.get('force_company'):
            sellers = sellers.filtered(lambda s: not s.company_id or s.company_id.id == self.env.context['force_company'])
        for seller in sellers:
            #Same test as in suoper()._select_seller, but we skip the test for quantity
            if seller.date_start and seller.date_start > date:
                continue
            if seller.date_end and seller.date_end < date:
                continue
            if partner_id and seller.name not in [partner_id, partner_id.parent_id]:
                continue
            if seller.product_id and seller.product_id != self:
                continue
            if not res or res.name == seller.name:
                res |= seller
        ##TODO: would we rather sort by price or by price * min_qty?  From a business flow it 
        #has to do with whether we have a high turnover (in which case we'd rather the lowest price per, becuase we know we'll use them)
        #or if we're goign to have a low turnover (and we just want the lowest cost of ownership becuase the excess will probably be written off)
        return res.sorted('price')[:1]

class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    increment_qty = fields.Float(
        'Order Increment', default=0.0,
        help="The increment in which the part must be ordered, expressed in the vendor Product Unit of Measure if not any, in the default unit of measure of the product otherwise.")
    round_up = fields.Boolean('Round to MOQ', default=False, help="If ticked, RFQ quantities will be adjusted to match MOQ and order increment.")  

    def round_to_moq(self, desired_qty):
        #By this point desired_qty is already in our UoM
        if self.round_up:
            moqed_qty = max(desired_qty, self.min_qty)

            if self.increment_qty: #this might not be set, or it might be 0.0 which means ignore/no increment
                precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')               
                excess = moqed_qty - self.min_qty
                exceess_incs = (excess//self.increment_qty)
                if float_compare(excess%self.increment_qty, 0.0, precision_digits=precision) == 1:
                    exceess_incs+=1
                to_order_qty = self.min_qty + (exceess_incs * self.increment_qty)
            else:
                to_order_qty = moqed_qty
        else:
            to_order_qty = desired_qty
        return to_order_qty
