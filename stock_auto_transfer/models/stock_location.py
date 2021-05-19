from odoo import api, models, fields

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
        #TODO: generate procurement for -forecast_qty in me for each stock in self _only_ (not in children of self) with forecast_qty < 0
        return {}       

    def run_auto_empty(self):
        self._auto_empty(None)
        return {}   

    def _auto_empty(self, target_product_ids):
        if self.auto_empty and self.auto_empty_target_id and self.auto_empty_operation_id:
            #stockkidloc = self.env['product.product'].with_context({'location': self.location_id.id, 'compute_child': False}).search([('virtual_available','>',0.0)])

            #stockloc = self.env['product.product'].with_context({'location': self.location_id.id, 'compute_child': True}).search([('virtual_available','>',0.0)])
            myloc = self.env['product.product'].with_context({},location=self.id, compute_child=False).search([('virtual_available','>',0.0)])
            stockkidloc = self.env['product.product'].with_context({},location=self.location_id.id, compute_child=False).search([('virtual_available','>',0.0)])
            stockloc = self.env['product.product'].with_context({},location=self.location_id.id, compute_child=True).search([('virtual_available','>',0.0)])
            #Gather all target_product_ids for which forecast_qty > 0
            #virtual_available

            #contxt: location, compute_child
            #new_picking = self.env['stock.picking'].create({
            #    'location_id': self.id,
            #    'location_dest_id': self.auto_empty_target_id.id,
            #    'picking_type_id': self.auto_empty_operation_id.id,
            #})
            #new_move = self.env['stock.move'].create({
            #    'name': 'test_link_assign_7',
            #    'location_id': self.id,
            #    'location_dest_id': self.auto_empty_target_id.id,
            #    'product_id': self.product.id,
            #    'product_uom_qty': 1.0,
            #    'picking_id': new_picking.id,
            #})            
            #TODO: Generate (and assign!) auto_empty_operation_id's for forecast_qty from me to auto_empty_target_id for product_id (or all products) in self _only_ (not in children of self) with forecast_qty > 0
            pass


            