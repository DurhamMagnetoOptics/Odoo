# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import UserError
from odoo.tools import float_compare

class StockMove(models.Model):
    _inherit = "stock.move"

    def _adjust_procure_method(self):
        super()._adjust_procure_method() #First check as normal.

        #Now we only want to consider cases where a more specific rule wasn't found, and the route has this option enabled
        gen = (move for move in self if (move.procure_method == 'make_to_stock' and move.picking_type_id.apply_parent_pull))
        for move in gen:
            product_id = move.product_id

            #Recursively build a list of all the parents up the chain
            loc_ids = []
            thisGen = move.location_id
            while thisGen.location_id: #check if a parent exists
                #if so, add it and move up a level
                loc_ids.append(thisGen.location_id.id)
                thisGen = thisGen.location_id

            #now use a search domain that includes all of the parents instead of an exact match to this source.    
            domain = [
                ('location_src_id', 'in', loc_ids),
                ('location_id', '=', move.location_dest_id.id),
                ('action', '!=', 'push')
            ]
            rules = self.env['procurement.group']._search_rule(False, product_id, move.warehouse_id, domain)
            if rules and (rules.procure_method == 'make_to_order'):
                move.procure_method = rules.procure_method
            else:
                move.procure_method = 'make_to_stock'
