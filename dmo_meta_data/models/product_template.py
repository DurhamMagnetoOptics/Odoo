# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools import float_compare

class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_revision = fields.Integer('Rev', help='Revision/Issue', default='')
    product_design_file_name = fields.Text('Design File', help='Name of CAD/vendor design file', default='')
    product_manufacturer = fields.Text('Manufacturer', help="Part's OEM", default='')
    product_manufacturer_part = fields.Text('Part Number', help="Manufacturer's Part Number", default='')
    product_CoO = fields.Many2one('res.country', 'COO', help='Country of Origin', store=True)