from odoo import models, fields

class StockMove(models.Model):
    _inherit = "stock.move"
    multilevel_kitting_name = fields.Char('Bin Name', help="If multilevel kitting is enabled, this sublocation of the source will be used as the name of the raw material location for the related stock move")