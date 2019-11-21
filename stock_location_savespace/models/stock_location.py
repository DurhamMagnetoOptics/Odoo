from odoo import models, fields

class Location(models.Model):
    _inherit = 'stock.location'

    putaway_savespace = fields.Boolean('Reuse bins', default=False, help="If no putaway rule is found, use existing stock location as the putaway strategy")

    def _get_putaway_strategy(self, product):
        ''' Returns the location where the product has to be put, if any compliant putaway strategy is found. Otherwise returns None.'''
        res = super()._get_putaway_strategy(product)
        if not res:
            local_product = product.with_context(location=self.id)
            if local_product.qty_available > 0.0:
                domain_quant, dummy, dummy = local_product._get_domain_locations()
                domain_quant += [('product_id', '=', local_product.id), ('quantity', '>', 0.0)]                
                quants = local_product.stock_quant_ids.search(domain_quant, order='in_date')
                if quants:
                    return quants[0].location_id
        return res