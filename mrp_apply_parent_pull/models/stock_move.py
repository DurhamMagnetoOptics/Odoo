# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import UserError
from odoo.tools import float_compare
"""
class StockMove(models.Model):
    _inherit = "stock.move"

    def _adjust_procure_method(self):
        super()._adjust_procure_method() #First check as normal.

        #Now we only want to consider cases where a more specific rule wasn't found
        gen = (move for move in self if move.procure_method == 'make_to_stock')
        for move in gen:
            product_id = move.product_id
            loc_ids = []
            domain = [
                ('location_src_id', '=', move.location_id.id),
                ('location_id', '=', move.location_dest_id.id),
                ('action', '!=', 'push')
            ]
            rules = self.env['procurement.group']._search_rule(False, product_id, move.warehouse_id, domain)
            if rules and (rules.procure_method == 'make_to_order'):
                move.procure_method = rules.procure_method
            else:
                move.procure_method = 'make_to_stock'
"""                
