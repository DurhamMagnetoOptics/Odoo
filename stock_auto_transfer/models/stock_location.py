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
        #TODO: Generate auto_empty_operation_id's for forecast_qty from me to auto_empty_target_id for product_id (or all products) in self _only_ (not in children of self) with forecast_qty > 0
        pass


            