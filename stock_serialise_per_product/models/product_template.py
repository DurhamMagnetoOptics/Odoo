# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools import float_compare

class ProductTemplate(models.Model):
    _inherit = "product.template"

    sequence_id = fields.Many2one('ir.sequence', 'Serialisation Sequence', check_company=True)
    