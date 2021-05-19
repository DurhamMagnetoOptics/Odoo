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
    
    def action_done(self):
        res = super().action_done()
        if self.location_dest_id.auto_empty:
            myprods = self.move_lines.product_id if self.move_lines else self.move_line_ids.product_id 
            if not myprods: return res
            self._unreserve_all_ephemeral(self.location_dest_id, myprods)
            self._reserve_all_ephemeral(self.location_dest_id, myprods)
            self.location_dest_id._auto_empty(myprods)
        return res

    def _get_ephemeral(self, states, target_location_id, target_product_ids):
        #We can do a lot less filtering than the similar OCA module, becuase we have the ephemeral flag to narrow
        # down our results, so there's no concern about picking moves that are part of an MTO chain, etc.
        pick_types = self.env['stock.picking.type'].search([('ephemeral','=',True)])
        pick_type_ids = pick_types.mapped('id')
        search_domains = [('picking_type_id','in',pick_type_ids),('state','in',states)]
        
        if target_location_id:
            search_domains.append(('location_id','=',target_location_id.id))
        
        picks = self.env['stock.picking'].search(search_domains, order='priority desc, scheduled_date asc')

        if target_product_ids:
            #picks = picks.filtered(lambda r: [pid for pid in r.move_lines.product_id.mapped('id') if pid in target_product_ids.mapped('id')])
            # the lambda function returns a (potentially empty) list of pids which appear in both recordsets, which filtred evalutes as a boolean
            #The forum says '&' is the intersection between recordsets, and since recordsets are truthy when not empty (same as lists, above), we can do this more efficiently.
            picks = picks.filtered(lambda r: r.move_lines.product_id & target_product_ids)
       
        return picks  

    def _reserve_all_ephemeral(self, target_location_id, target_product_ids):
        target_picks = self._get_ephemeral(['waiting','confirmed','assigned'], target_location_id, target_product_ids) #include assigned because a picking will be 'assigned' if its moves are mix of assigned and confirmed.
        if target_picks:
            target_picks.action_assign()

    def _unreserve_all_ephemeral(self, target_location_id, target_product_ids):
        target_picks = self._get_ephemeral(['assigned'], target_location_id, target_product_ids)
        if target_picks:
            target_picks.do_unreserve()       