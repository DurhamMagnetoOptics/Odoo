# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools import float_compare

class ProductTemplate(models.Model):
    _inherit = "product.template"

    link_BOM_to_lot = fields.Boolean('Automatically link BOM to lot/serial', default=False)
