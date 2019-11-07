# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict
from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

class StockRule(models.Model):
    _inherit = 'stock.rule'

    procure_method = fields.Selection(selection_add=[('mts_else_alt', 'Take from stock; if shoftfall, trigger alternate rule')])

    alternate_rule_id = fields.Many2one('stock.rule', string="Alternate Rule")

    def _get_message_dict(self):
        """ Return a dict with the different possible message used for the
        rule message. It should return one message for each stock.rule action
        (except push and pull). This function is override in mrp and
        purchase_stock in order to complete the dictionary.
        """
        message_dict = super()._get_message_dict()
        if self.procure_method == 'mts_else_alt' and self.location_src_id:
            source, destination, operation = self._get_message_values()     
            suffix = "<br>If the products are not available in <b>%s</b>, the alternate rule will be triggered." % source
            message_dict['pull'] = 'When products are needed in <b>%s</b>, <br/> <b>%s</b> are created from <b>%s</b> to fulfill the need.' % (destination, operation, source) + suffix
        return message_dict    

    def _run_pull(self, procurements):
        #Original block from Odoo stock_rule.py
        moves_values_by_company = defaultdict(list)
        mtso_products_by_locations = defaultdict(list)

        # To handle the `mts_else_mto` procure method, we do a preliminary loop to
        # isolate the products we would need to read the forecasted quantity,
        # in order to to batch the read. We also make a sanitary check on the
        # `location_src_id` field.
        for procurement, rule in procurements:
            if not rule.location_src_id:
                msg = _('No source location defined on stock rule: %s!') % (rule.name, )
                raise UserError(msg)

            if rule.procure_method in {'mts_else_mto', 'mts_else_alt'}:
                mtso_products_by_locations[rule.location_src_id].append(procurement.product_id.id)

        # Get the forecasted quantity for the `mts_else_mto` procurement.
        forecasted_qties_by_loc = {}
        for location, product_ids in mtso_products_by_locations.items():
            products = self.env['product.product'].browse(product_ids).with_context(location=location.id)
            forecasted_qties_by_loc[location] = {product.id: product.virtual_available for product in products}

        # Prepare the move values, adapt the `procure_method` if needed.
        for procurement, rule in procurements:
            #Handle the new procurement method
            if rule.procure_method == 'mts_else_alt':
                qty_needed = procurement.product_uom._compute_quantity(procurement.product_qty, procurement.product_id.uom_id)
                qty_available = forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id]
                qty_shortfall = qty_needed - qty_available
                if float_compare(qty_shortfall, 0, precision_rounding=procurement.product_id.uom_id.rounding) <= 0:   #1 means first numeber biger than second, 0 means equal, -1 means first number smaller than second; 
                    #Execute the existing rule (mto_else_alt's source and location and type) as 'take from stock' for full qty
                    forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_needed

                    move_values = rule._get_stock_move_values(*procurement)
                    move_values['procure_method'] = 'make_to_stock'
                    moves_values_by_company[procurement.company_id.id].append(move_values)
                elif float_compare(qty_available, 0, precision_rounding=procurement.product_id.uom_id.rounding) > 0:   #1 means first numeber biger than second, 0 means equal, -1 means first number smaller than second; 
                    #Execute the existing rule (mto_else_alt's source and location and type) as take from stock for the amount in stock
                    forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_available

                    procurement1 = procurement._replace(product_qty=qty_available) #procurement is a named tuple, so we make a copy with one altered value
                    move_values = rule._get_stock_move_values(*procurement1)
                    move_values['procure_method'] = 'make_to_stock'
                    moves_values_by_company[procurement.company_id.id].append(move_values)  

                    #Execute the alternate rule for the shortfall
                    procurement2 = procurement._replace(product_qty=qty_shortfall)
                    move_values = rule.alternate_rule_id._get_stock_move_values(*procurement2)
                    moves_values_by_company[procurement.company_id.id].append(move_values)                                        
                else:
                    #Execute the alternate rule for the full qty
                    move_values = rule.alternate_rule_id._get_stock_move_values(*procurement)
                    moves_values_by_company[procurement.company_id.id].append(move_values)                    
            else:
                #Original block from Odoo stock_rule.py
                procure_method = rule.procure_method
                if rule.procure_method == 'mts_else_mto':
                    qty_needed = procurement.product_uom._compute_quantity(procurement.product_qty, procurement.product_id.uom_id)
                    qty_available = forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id]
                    if float_compare(qty_needed, qty_available, precision_rounding=procurement.product_id.uom_id.rounding) <= 0:
                        procure_method = 'make_to_stock'
                        forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_needed
                    else:
                        procure_method = 'make_to_order'

                move_values = rule._get_stock_move_values(*procurement)
                move_values['procure_method'] = procure_method
                moves_values_by_company[procurement.company_id.id].append(move_values)

        #Original block from Odoo stock_rule.py
        for company_id, moves_values in moves_values_by_company.items():
            # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            moves = self.env['stock.move'].sudo().with_context(force_company=company_id).create(moves_values)
            # Since action_confirm launch following procurement_group we should activate it.
            moves._action_confirm()
        return True