from odoo import models, fields

class Location(models.Model):
    _inherit = 'stock.location'

    putaway_savespace = fields.Boolean('Reuse bins', default=False, help="If no putaway rule is found, use existing stock location as the putaway strategy")

    def _get_putaway_strategy(self, product):
        ''' Returns the location where the product has to be put, if any compliant putaway strategy is found. Otherwise returns None.'''
        res = super()._get_putaway_strategy(product)
        if not res:
            #TODO search my children for any stock, and if found return one of their locations

            #quants = self.env['stock.quant'].search([('product_id','=',product.id),('quantity', '>', 0.0)])
            #my_quants = quants.with_context(location=self)
            #if my_quants:
            #    return my_quants[0].location_id
        return res