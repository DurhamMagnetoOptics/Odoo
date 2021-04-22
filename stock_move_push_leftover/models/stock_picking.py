

from odoo import models, fields

class PickingType(models.Model):
    _inherit = "stock.picking.type"
    push_leftover = fields.Boolean('Push Leftovers', default=False, help="If ticked, push rules are applied to any quantity not accounted for by the next move in the chain")
    merge_procure_method = fields.Boolean('Merge Methods', default=False, help="If ticked, stock moves are merged even if their procurement methods do not match")
    merge_created_PO = fields.Boolean('Merge POs', default=False, help="If ticked, stock moves are merged even if their created purchase lines do not match")