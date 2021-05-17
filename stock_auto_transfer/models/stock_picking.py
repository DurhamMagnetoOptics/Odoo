# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class PickingType(models.Model):
    _inherit = "stock.picking.type"

    ephemeral = fields.Boolean('Ephemeral', default=False)

    @api.model
    def run_cancel_ephemeral(self):
        self._cancel_ephemeral(None, None)
        return {}      

    @api.model
    def _cancel_ephemeral(self, target_location_id, target_product_ids):
        target_ops = []
        if target_location_id and target_product_ids:
            pass
            #TODO append all operations of my type from location_id containig product_ids
        elif target_location_id:
            pass
            #TODO append all operations of my type from location_id
        elif target_product_ids:
            pass
            #TODO append all operations of my type containig product_ids
        else:
            pass
            #TODO append all operations of my type
        #TODO: cancel all target_ops
        pass
        return {}   

class Picking(models.Model):
    _inherit = "stock.picking"

    def action_done(self):
        res = super().action_done
        if self.location_dest_id.auto_empty:
            self.picking_type_id._cancel_ephemeral(self.location_dest_id, self.move_line_ids.product_id)
            self._assign_related(self.location_dest_id, self.move_line_ids.product_id)
            self.location_dest_id._auto_empty(self.move_line_ids.product_id)
        return res

    def _assign_related(self, target_location_id, target_product_ids):
        #TODO stock_pikcing.action_assign for each stock_picking of my type, whose source location matches target_location_id, and who product list overlaps with target_product_ids
        return {}