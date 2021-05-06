# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from odoo.tools import float_compare
from odoo.exceptions import UserError, ValidationError

class StockRule(models.Model):
    _inherit = 'stock.rule'

    clear_group = fields.Boolean(
        'Empty Procurement Group', default=False,
        help="When ticked, procurement group will be left empty, instead of being copied form the preceeding move.")

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        new_move_vals = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        if self.clear_group:
            new_move_vals['group_id']=False
        return new_move_vals