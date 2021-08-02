from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"
    
    require_ref = fields.Boolean(default=False)