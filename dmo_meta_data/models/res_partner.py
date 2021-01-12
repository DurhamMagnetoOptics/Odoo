# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    vendor_short_code = fields.Text('Short code (DMO code prefix) for this vendor', default='')
    vendor_clipboard_style = fields.Integer('Enumeration describing the text format for manual orders', default='')
