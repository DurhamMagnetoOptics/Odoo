from odoo import api, fields, models

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom):
        res = super()._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom)
        if self.picking_type_id.multilevel_kitting and bom.multilevel_kitting_name:
            #Does the location already exist?
            new_loc = self.env['stock.location']

            for loc in location_id.child_ids: #if yes, find it
                if loc.name == bom.multilevel_kitting_name:
                    new_loc = loc
                    break
            if not new_loc:
                #If no, create it.
                new_loc = new_loc.create({
                    'name': bom.multilevel_kitting_name,
                    'location_id': location_id.id
                })  
            res['location_src_id'] = new_loc.id
        return res