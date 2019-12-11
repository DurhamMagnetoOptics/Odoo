# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools import float_compare

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.depends('product_id')
    def _compute_name(self):
        for lot in self:
            if not lot.name and lot.product_id:
                if lot.product_id.sequence_id:
                    lot.name = lot.product_id.sequence_id._next()
                else:
                    #In this case return the default as written in the stock module
                    lot.name = lot.env['ir.sequence'].next_by_code('stock.lot.serial')

    #keep the existing name field, but change the default to empty string.  Setting the default to False causes an error as name can't be Null. I guess SQL differentiates between null and the empty string.
    name = fields.Char(default='', compute="_compute_name", store=True, readonly=False)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._compute_name()
        return res
    