# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.exceptions import UserError

class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    increment_qty = fields.Float(
        'Increment Quantity', default=0.0, required=True,
        help="The increment in which the part must be ordered, expressed in the vendor Product Unit of Measure if not any, in the default unit of measure of the product otherwise.")
    round_up = fields.Boolean('Round up to MOQ', default=False, help="If ticked, RFQ quantities will be adjusted to match MOQ and order increment.")        
