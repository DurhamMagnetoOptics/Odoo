# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools import float_compare

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    def _default_name(self):
        if self.product_id and self.product_id.sequence_id:
            return self.product_id.sequence_id._next()
        else:
            #In this case return the default as written in the stock module
            return self.env['ir.sequence'].next_by_code('stock.lot.serial')

    #keep the existing name field, but change the default
    name = fields.Char(default = lambda self: self._default_name())
    