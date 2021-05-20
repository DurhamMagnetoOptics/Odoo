# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class PickingType(models.Model):
    _inherit = "stock.picking.type"

    ephemeral = fields.Boolean('Ephemeral', default=False)