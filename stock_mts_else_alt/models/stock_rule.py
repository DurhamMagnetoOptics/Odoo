# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from odoo.tools import float_compare
from odoo.exceptions import UserError, ValidationError

class StockRule(models.Model):
    _inherit = 'stock.rule'

    action = fields.Selection(selection_add=[('branch', 'Branch')])

    alternate_rule_id = fields.Many2one('stock.rule', string="Alternate Rule")

    @api.constrains('location_id','alternate_rule_id')
    def _constrain_branch_location(self):
        for stockrule in self:
            if stockrule.alternate_rule_id:
                if stockrule.location_id.id != stockrule.alternate_rule_id.location_id.id:
                    raise ValidationError('The alternate rule destination location must match the primary rule destination location')   #this would mean that the procurement matched to the primary rule won't actually be satisfied by the alternate rule
                if stockrule.location_id.id == stockrule.alternate_rule_id.location_src_id.id:
                    raise ValidationError('The alternate rule source location should not match the primary rule destination location')  #this would lead to an infinite loop as the alternate rule triggers the primary rule   

    @api.constrains('action', 'procure_method')
    def _constrain_branch_procure_method(self):
        for stockrule in self:
            if stockrule.action == 'branch' and stockrule.procure_method not in ('make_to_stock', 'make_to_order'):
                raise ValidationError('The primary rule must be simple MTS or MTO')   #we execute pull on the prime rule directly, so it's procure method needs to be directly actionable (aka not mts_else_mto)           


    def _get_message_dict(self):
        message_dict = super(StockRule, self)._get_message_dict()
        source, destination, operation = self._get_message_values()  
        suffix = "<br>If the products are not available in <b>%s</b>, the alternate rule will be triggered." % source
        branch_message = 'When products are needed in <b>%s</b>, <br/> <b>%s</b> are created from <b>%s</b> to fulfill the need.' % (destination, operation, source) + suffix
        message_dict.update({
            'branch': branch_message
        })
        return message_dict


    @api.model
    def _run_branch(self, procurements):
        for procurement, rule in procurements:
            if not rule.location_src_id:
                msg = _('No source location defined on stock rule: %s!') % (rule.name, )
                raise UserError(msg)

            localized_product = procurement.product_id.with_context(location=rule.location_src_id.id)
            qty_available = localized_product.virtual_available
            qty_needed = procurement.product_uom._compute_quantity(procurement.product_qty, procurement.product_id.uom_id)
            qty_shortfall = qty_needed - qty_available   

            if float_compare(qty_shortfall, 0, precision_rounding=procurement.product_id.uom_id.rounding) <= 0:   #1 means first numeber biger than second, 0 means equal, -1 means first number smaller than second; 
                #Execute the existing rule (mto_else_alt's source and location and type) as 'take from stock' for full qty
                rule._run_pull([(procurement, rule)])
            elif float_compare(qty_available, 0, precision_rounding=procurement.product_id.uom_id.rounding) > 0:   #1 means first numeber biger than second, 0 means equal, -1 means first number smaller than second; 
                #Execute the existing rule (mto_else_alt's source and location and type) as take from stock for the amount in stock
                procurement1 = procurement._replace(product_qty=qty_available) #procurement is a named tuple, so we make a copy with one altered value
                rule._run_pull([(procurement1, rule)]) 

                #Execute the alternate rule for the shortfall
                procurement2 = procurement._replace(product_qty=qty_shortfall)
                if hasattr(rule.alternate_rule_id, '_run_%s' % rule.alternate_rule_id.action):
                    try:
                        getattr(rule.alternate_rule_id, '_run_%s' % rule.alternate_rule_id.action)([(procurement2, rule.alternate_rule_id)])
                    except UserError as e:
                        raise UserError(e.name)
                else:
                    UserError("The method _run_%s doesn't exist on the procurement rules" % rule.alternate_rule_id.action)
            else:
                #Execute the alternate rule for the full qty
                if hasattr(rule.alternate_rule_id, '_run_%s' % rule.alternate_rule_id.action):
                    try:
                        getattr(rule.alternate_rule_id, '_run_%s' % rule.alternate_rule_id.action)([(procurement, rule.alternate_rule_id)])
                    except UserError as e:
                        raise UserError(e.name)
                else:
                    UserError("The method _run_%s doesn't exist on the procurement rules" % rule.alternate_rule_id.action)
        return True