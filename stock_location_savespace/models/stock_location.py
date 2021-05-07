from odoo import models, fields, _
from odoo.exceptions import UserError

class Location(models.Model):
    _inherit = 'stock.location'

    putaway_savespace = fields.Boolean('Reuse bins', default=False, help="If no putaway rule is found, use existing stock location as the putaway strategy")

    def _dummyget_putaway_strategy(self, product):
        ''' Returns the location where the product has to be put, if any compliant putaway strategy is found. Otherwise returns None.'''
        res = super()._get_putaway_strategy(product)
        if not res and self.putaway_savespace:
            local_product = product.with_context(location=self.id)
            if local_product.qty_available > 0.0:
                domain_quant, dummy, dummy = local_product._get_domain_locations()
                domain_quant += [('product_id', '=', local_product.id), ('quantity', '>', 0.0)]                
                quants = local_product.stock_quant_ids.search(domain_quant, order='in_date')
                if quants:
                    return quants[0].location_id
        return res

    def _get_putaway_strategy(self, product):
        res = super()._get_putaway_strategy(product)
        if not res and self.putaway_savespace:
            local_product = product.with_context(location=self.id)
            if local_product.qty_available > 0.0:        

                #if there's more than one location, choose using the same logic that we'd use for what stock to draw
                removal_strategy = self.env['stock.quant']._get_removal_strategy(product, self)
                if removal_strategy == 'fifo':
                    sort_order = 'in_date'
                elif removal_strategy == 'lifo':
                    sort_order = 'in_date desc'
                else:
                    raise UserError(_('Removal strategy %s not implemented in stock_location_savespace.') % (removal_strategy,))

                domain_quant, dummy, dummy = local_product._get_domain_locations()
                domain_quant += [('product_id', '=', local_product.id), ('quantity', '>', 0.0)]                
                quants = local_product.stock_quant_ids.search(domain_quant, order=sort_order)
                if quants:
                    return quants[0].location_id  
        return res              