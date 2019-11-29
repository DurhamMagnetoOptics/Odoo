# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools import float_compare

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    ##TODO: add a contraint to make sure this matches the product.  Ideally the drop down would only display valid ones,
    # and maybe even nothing until the product is set.  Can it autopopulate when product is chosen?
    # We ought to be able to steal all of that functionality from the Manufacturing Order view.
    bom_id = fields.Many2one('mrp.bom', 'Bill of Materials', check_company=True)
    