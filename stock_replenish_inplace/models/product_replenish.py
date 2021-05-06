import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context

class ProductReplenish(models.TransientModel):
    _inherit = 'product.replenish'

    override_location_id = fields.Many2one('stock.location', 'Location', check_company=True)
    
    def launch_replenishment(self):
        if self.override_location_id:
            #This is super's launch_replenishment, with the location changed.  Odoo create's the procurement data (with location hard-coded to the warehouose default stock location) and
            # runs the procurement in one go, so I don't see a way around it except to cut-and-paste their code. If this ever breaks the first thing to check is if product_replenish's
            # launch_replenishment has changed from below

            ##start cut-and-paste of odoo/stock/addons/wizard/product_replenish.py:ProductReplenish.launch_replenishment()
            uom_reference = self.product_id.uom_id
            self.quantity = self.product_uom_id._compute_quantity(self.quantity, uom_reference)
            try:
                self.env['procurement.group'].with_context(clean_context(self.env.context)).run([
                    self.env['procurement.group'].Procurement(
                        self.product_id,
                        self.quantity,
                        uom_reference,
                        self.override_location_id,  ### Location -- this is the only line we actually need to change
                        _("Manual Replenishment"),  # Name
                        _("Manual Replenishment"),  # Origin
                        self.warehouse_id.company_id,
                        self._prepare_run_values()  # Values
                    )
                ])
            except UserError as error:
                raise UserError(error)    
            ##End cut-and-paste        
        else:
            super().launch_replenishment()
