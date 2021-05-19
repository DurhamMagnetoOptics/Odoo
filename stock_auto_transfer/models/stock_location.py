from odoo import api, models, fields
from odoo.tools.misc import clean_context

class Location(models.Model):
    _inherit = 'stock.location'

    auto_fulfill = fields.Boolean('Auto Fulfill', default=False, help="Automatically generate procurements to meet stock shortfalls")   

    auto_empty = fields.Boolean('Auto Empty', default=False, help="Automatically generate Operations to remove stock excess")
    auto_empty_target_id = fields.Many2one('stock.location', string="Send excess to") 
    auto_empty_operation_id = fields.Many2one('stock.picking.type', string="Send excess using")   

    def run_auto_fulfill(self):
        #depth-first so the procurement location is as specific as possible
        for c_id in self.child_ids:
            c_id.run_auto_fulfill()
        #Once children are done, do me      
        self._auto_fulfill()

    def _auto_fulfill(self):
        if self.auto_fulfill:
            #TODO: totally untested!
            shortfall_products = self.env['product.product'].with_context({},location=self.id, compute_child=False).search([('virtual_available','<',0.0)])
            procs = []
            for prod in shortfall_products:
                new_proc = self.env['procurement.group'].Procurement(
                            prod,
                            -prod.virtual_available,
                            prod.uom_id,
                            self,
                            "Auto Replenishment",
                            "Auto Replenishment",
                            self.company_id,
                            {}
                        )
                procs.append(new_proc)
            if procs:
                self.env['procurement.group'].with_context(clean_context(self.env.context)).run([procs])

    def run_auto_empty(self):
        self._auto_empty(None)
        return {}   

    def _auto_empty(self, target_product_ids):
        if self.auto_empty and self.auto_empty_target_id and self.auto_empty_operation_id:
            #TODO: totally untested!
            excess_products = self.env['product.product'].with_context({},location=self.id, compute_child=False).search([('virtual_available','>',0.0)])
            relevant_excess_products = (excess_products & target_product_ids) if target_product_ids else excess_products

            #TODO: Can I create just moves and let Odoo automatically build up the picking??
            for prod in relevant_excess_products:
                new_move = self.env['stock.move'].create({
                    'location_id': self.id,
                    'location_dest_id': self.auto_empty_target_id.id,
                    'product_id': prod.id,
                    'product_uom': prod.uom_id.id,
                    'product_uom_qty': prod.virtual_available,
                    'picking_type_id': self.auto_empty_operation_id.id
                })  
                new_move._action_confirm()
                new_move._action_assign()
            pass


            