# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class PickingType(models.Model):
    _inherit = "stock.picking.type"

    ephemeral = fields.Boolean('Ephemeral', default=False)


class Picking(models.Model):
    _inherit = "stock.picking"

    #wTODO: add multi-select actions to the drop-down menu for:
    #action_assign
    #do_unreserve
    #action_cancel

    def action_done(self):
        res = super().action_done()
        if self.location_dest_id and self.location_dest_id.auto_empty:
            self._unreserve_all_ephemeral(self.location_dest_id, self.move_line_ids.product_id)
            self._reserve_all_ephemeral(self.location_dest_id, self.move_line_ids.product_id)
            self.location_dest_id._auto_empty(self.move_line_ids.product_id)
        return res

    def _get_ephemeral(self, states, target_location_id, target_product_ids):
        pick_types = self.env['stock.picking.types'].search([('ephemeral','=',True)])
        pick_type_ids = pick_types.mapped('id')
        search_domains = [('picking_type_id','in',pick_type_ids),('state','in',states)]
        
        #Note: move_lines are the stock.moves, and picks.move_line_ids are the stock.move.lines.
        # For planned transfers, move_lines exist immediate and move_line_ids are only filled in once moves are reserved.
        # For immediate transfers, there could be no move_lines, and only move_line_ids 
        # On the other hand, for immediate transfers they'll never be in the waiting/confirmed/assigned states, only draft/done/cancelled.  So they're irrelevant here.
        if target_location_id:
            search_domains.append(('location_id','=',target_location_id.id))
        elif target_product_ids:
            pass
            #TODO append all operations of my type containig product_ids in their move_lines to domain.  Can we??

        picks = self.env['stock.picking'].search(search_domains)               
        return picks.mapped('id')  

    def _reserve_all_ephemeral(self, target_location_id, target_product_ids):
        target_pick_ids = self._get_ephemeral(['waiting','confirmed'], target_location_id, target_product_ids)
        target_picks = self.env['stock.picking'].browse(target_pick_ids)
        target_picks.action_assign()
        return {} 

    def _unreserve_all_ephemeral(self, target_location_id, target_product_ids):
        target_pick_ids = self._get_ephemeral(['assigned'], target_location_id, target_product_ids)
        target_picks = self.env['stock.picking'].browse(target_pick_ids)
        target_picks.do_unreserve()
        return {}          