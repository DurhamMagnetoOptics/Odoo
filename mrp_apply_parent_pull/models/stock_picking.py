

from odoo import models, fields

class PickingType(models.Model):
    _inherit = "stock.picking.type"
    apply_parent_pull = fields.Boolean('MRP: MTO from parent', default=False, help="If ticked, rules on the parent locations will also be checked to determine if an MRP-driven procurement should be set to MTO")