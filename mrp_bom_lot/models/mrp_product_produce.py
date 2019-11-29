# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"
    bom_id = fields.Many2one('mrp.bom', 'Bill of Materials', related='production_id.bom_id')
    
    #Change the lot domain to require matching BOM, if enabled   
    @api.onchange('product_id', 'bom_id')
    def apply_lot_domain(self):
        if self.product_id.link_BOM_to_lot:
            dom = "[('product_id', '=', product_id), ('company_id', '=', company_id), ('bom_id', '=', bom_id)]"
        else:
            dom = "[('product_id', '=', product_id), ('company_id', '=', company_id)]"
        return {'domain': {'finished_lot_id': dom}}
