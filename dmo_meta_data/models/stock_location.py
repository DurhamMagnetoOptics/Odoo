from odoo import api, fields, models, _

class Location(models.Model):
    _inherit = "stock.location"

    storageSize = fields.Char('Storage Size', required=False)