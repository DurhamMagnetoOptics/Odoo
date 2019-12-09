# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools import float_compare

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    _my_name = ''

    @api.depends('product_id')
    def _compute_name(self):
        for lot in self:
            if not lot._my_name:
                if not lot.product_id:
                    lot._my_name = ''
                else:
                    if lot.product_id.sequence_id:
                        lot._my_name = lot.product_id.sequence_id._next()
                    else:
                        #In this case return the default as written in the stock module
                        lot.my_name = lot.env['ir.sequence'].next_by_code('stock.lot.serial')
            lot.name = lot._my_name

    def _inverse_name(self):
        for lot in self:
            lot._my_name = lot.name

    #keep the existing name field, but change the default
    name = fields.Char(compute="_compute_name", inverse="_inverse_name", store=True, readonly=False)
    