# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class PickingType(models.Model):
    _inherit = "stock.picking.type"

    ephemeral = fields.Boolean('Ephemeral', default=False)


class Picking(models.Model):
    _inherit = "stock.picking"

    #Note: move_lines are the stock.moves, and picks.move_line_ids are the stock.move.lines.
    # For planned transfers, move_lines exist immediate and move_line_ids are only filled in once moves are reserved.
    # For immediate transfers, there could be no move_lines, and only move_line_ids 
    # On the other hand, for immediate transfers they'll never be in the waiting/confirmed/assigned states, only draft/done/cancelled.  So they're irrelevant here.
    
    def action_done(self):
        res = super().action_done()
        if self.location_dest_id and self.location_dest_id.auto_empty:
            self._unreserve_all_ephemeral(self.location_dest_id, self.move_lines.product_id)
            self._reserve_all_ephemeral(self.location_dest_id, self.move_lines.product_id)
            self.location_dest_id._auto_empty(self.move_lines.product_id)
        return res

    def _get_ephemeral(self, states, target_location_id, target_product_ids):
        #We can do a lot less filtering than the similar OCA module, becuase we have the ephemeral flag to narrow
        # down our results, so there's no concern about picking moves that are part of an MTO chain, etc.
        pick_types = self.env['stock.picking.types'].search([('ephemeral','=',True)])
        pick_type_ids = pick_types.mapped('id')
        search_domains = [('picking_type_id','in',pick_type_ids),('state','in',states)]
        
        if target_location_id:
            search_domains.append(('location_id','=',target_location_id.id))
        
        picks = self.env['stock.picking'].search(search_domains)

        if target_product_ids:
            #picks = picks.filtered(lambda r: [pid for pid in r.move_lines.product_id.mapped('id') if pid in target_product_ids.mapped('id')])
            # the lambda function returns a (potentially empty) list of pids which appear in both recordsets, which filtred evalutes as a boolean
            #The forum says '&' is the intersection between recordsets, and since recordsets are truthy when not empty (same as lists, above), we can do this more efficiently.
            picks = picks.filtered(lambda r: r.move_lines.product_id & target_product_ids)
       
        return picks  

    def _reserve_all_ephemeral(self, target_location_id, target_product_ids):
        target_picks = self._get_ephemeral(['waiting','confirmed'], target_location_id, target_product_ids)
        target_picks.action_assign()
        return {} 

    def _unreserve_all_ephemeral(self, target_location_id, target_product_ids):
        target_picks = self._get_ephemeral(['assigned'], target_location_id, target_product_ids)
        target_picks.do_unreserve()
        return {}          