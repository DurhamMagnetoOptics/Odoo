

from odoo import models, fields

class MrpBom(models.Model):
    _inherit = "mrp.bom"
    multilevel_kitting = fields.Boolean('Multilevel BOM Kitting', default=True, help="If ticked, Manufacturing Order raw mateial locations reflect the multilevel BOM hierarchy")

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    multilevel_kitting_name = fields.Char('Bin Name', help="If multilevel kitting is enabled, this sublocation of the source will be used as the name of the raw material location for the related stock move")
    