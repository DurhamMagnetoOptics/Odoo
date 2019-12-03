# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"
    bom_id = fields.Many2one('mrp.bom', 'Bill of Materials', store=False, compute='_compute_bom_id')


    #Change the lot domain to require matching BOM, if enabled   
    @api.onchange('product_id', 'bom_id')
    def apply_lot_domain(self):
        if self.product_id.link_BOM_to_lot:
            dom = "[('product_id', '=', product_id), ('company_id', '=', company_id), ('bom_id', '=', bom_id)]"
        else:
            dom = "[('product_id', '=', product_id), ('company_id', '=', company_id)]"
        return {'domain': {'finished_lot_id': dom}}

    @api.depends('product_id','production_id.bom_id')
    def _compute_bom_id(self):
        for wiz in self:
            if wiz.product_id and wiz.product_id.link_BOM_to_lot and wiz.production_id and wiz.production_id.bom_id:
                wiz.bom_id = wiz.production_id.bom_id
            else: 
                wiz.bom_id = False

    def action_generate_serial(self):
        res = super().action_generate_serial()
        self.finished_lot_id.bom_id = self.bom_id
        return res              
