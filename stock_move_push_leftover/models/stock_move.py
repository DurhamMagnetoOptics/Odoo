# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import UserError
from odoo.tools import float_compare

class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_split_vals(self, qty):
        vals = super()._prepare_move_split_vals(qty)
        if self.env.context.get('do_not_attach_child_moves'):
            vals['move_dest_ids'] = []
        return vals
    
    def _push_apply(self):
        super()._push_apply()

        #Then go back and check the cases parent skipped.
        for move in self:
            if move.move_dest_ids and move.picking_type_id.push_leftover:
                #In this case our parent function did nothing, so we need to test if there are leftover parts
                
                decimal_precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                #todo caluclate leftover quantity, in product UoM
                leftover_qty = move.product_uom_qty
                for child_move in move.move_dest_ids:
                    leftover_qty -= child_move.product_uom_qty
                if float_compare(leftover_qty, 0, precision_digits=decimal_precision) == 1:
                    move.with_context(do_not_attach_child_moves=1)._split(qty=leftover_qty)  # split confirms the action, which in turn runs the push.
