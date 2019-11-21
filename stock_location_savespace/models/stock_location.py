from odoo import models, fields

class Location(models.Model):
    _inherit = 'stock.location'

    putaway_savespace = fields.Boolean('Reuse bins', default=False, help="If no putaway rule is found, use existing stock location as the putaway strategy")

    def _get_putaway_strategy(self, product):
        ''' Returns the location where the product has to be put, if any compliant putaway strategy is found. Otherwise returns None.'''
        res = super()._get_putaway_strategy(product)
        if not res:
            #TODO search my children for any stock, and if found return one of their locations
            res = self.env['stock.location']
        return res