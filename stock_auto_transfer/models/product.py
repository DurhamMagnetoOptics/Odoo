from odoo import api, fields, models, _

class Product(models.Model):
    _inherit = "product.product"

    @api.depends_context(
        'compute_child', 
    )
    def _compute_quantities(self):
        #Odoo doesn't include 'compute_child' in the context dependencies, which means if you change compute_child withouot changing anything else about the context, it doesn't rerun the compute, and values are wrong.
        #Presumably that's just a bug, but for now it's faster to fix it here then to go through their reporting.
        return super()._compute_quantities()