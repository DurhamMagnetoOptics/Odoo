from odoo import api, fields, models

class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def run_unreserve_ephemeral(self):
        return self._unreserve_all_ephemeral(None, None)    

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder)
        for move in self:
            if move.location_dest_id.auto_empty and not move.move_dest_ids and move.product_id.type == 'product':
                move._unreserve_all_ephemeral(move.location_dest_id, move.product_id)
                move._reserve_all_ephemeral(move.location_dest_id, move.product_id)
                move.location_dest_id._auto_empty(move.product_id)
        return res

    @api.model
    def _get_ephemeral(self, states, target_location_id, target_product_id):
        #We can do a lot less filtering than the similar OCA module, becuase we have the ephemeral flag to narrow
        # down our results, so there's no concern about picking moves that are part of an MTO chain, etc.
        pick_types = self.env['stock.picking.type'].search([('ephemeral','=',True)])
        pick_type_ids = pick_types.mapped('id')
        search_domains = [('picking_type_id','in',pick_type_ids),('state','in',states),("move_orig_ids", "=", False),("procure_method", "=", "make_to_stock")]
        
        if target_location_id:
            search_domains.append(('location_id','=',target_location_id.id))

        if target_product_id:
            search_domains.append(('product_id','=',target_product_id.id))            
        
        moves = self.env['stock.move'].search(search_domains, order='priority desc, date_expected asc')

        #if target_product_ids:
        #    #The forum says '&' is the intersection between recordsets, and recordsets are fasly when empty and truthy any other time.
        #    moves = moves.filtered(lambda r: r.product_id & target_product_ids)
       
        return moves  

    @api.model
    def _reserve_all_ephemeral(self, target_location_id, target_product_id):
        target_moves = self._get_ephemeral(['waiting','confirmed','partially_available'], target_location_id, target_product_id) #include assigned to catch part-reserved.
        if target_moves:
            target_moves._action_assign()
            return True
        else:
            return False

    @api.model
    def _unreserve_all_ephemeral(self, target_location_id, target_product_id):
        target_moves = self._get_ephemeral(['partially_available','assigned'], target_location_id, target_product_id)
        if target_moves:
            target_moves._do_unreserve()   
            return True
        else:
            return False     