

from odoo import models, fields

class PickingType(models.Model):
    _inherit = "stock.picking.type"
    multilevel_kitting = fields.Boolean('Multilevel BOM Kitting', default=False, help="If ticked, Manufacturing Order raw mateial locations reflect the multilevel BOM hierarchy")