from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"
    
    require_ref = fields.Boolean(related='company_id.require_ref')