

from odoo import models, fields

class PickingType(models.Model):
    _inherit = "stock.picking.type"
    push_leftover = fields.Boolean('Push Leftovers', default=False, help="If ticked, push rules are applied to any quantity not accounted for by the next move in the chain")