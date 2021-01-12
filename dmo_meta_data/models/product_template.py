# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools import float_compare

class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_revision = fields.Integer('Revision/Issue', default='')
    product_design_file_name = fields.Text('Name of vendor design file', default='')
    product_manufacturer = fields.Text('Manufacturer', default='')
    product_manufacturer_part = fields.Text('Manufacturer Part Number', default='')
    product_CoO = fields.Many2one('res.country', 'Country of Origin', store=True)