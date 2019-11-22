

from odoo import models, fields

class MrpBom(models.Model):
    _inherit = "mrp.bom"
    multilevel_kitting_name = fields.Char('Multilevel BOM Kitting', help="If multilevel kitting is enabled, this sublocation will be used as the raw material location for MOs")