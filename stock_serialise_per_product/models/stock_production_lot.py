# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools import float_compare

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.depends('product_id')
    @api.constrains('product_id')  #Need to add the constrains decorator so it's also executed on create and write operations.  Depends on executes from changes in the ORM.
    def _compute_name(self):
        for lot in self:
            if not lot.name and lot.product_id:
                if lot.product_id.sequence_id:
                    lot.name = lot.product_id.sequence_id._next()
                else:
                    #In this case return the default as written in the stock module
                    lot.name = lot.env['ir.sequence'].next_by_code('stock.lot.serial')

    #keep the existing name field, but change the default
    name = fields.Char(default=False, compute="_compute_name", store=True, readonly=False)
    