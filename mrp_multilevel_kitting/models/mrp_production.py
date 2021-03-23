from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def create_and_set_sublocations(self):
        for production in self:
            if production.picking_type_id and production.bom_id and production.picking_type_id.multilevel_kitting and production.bom_id.multilevel_kitting:
                sublocation_dict = {}
                for mv in production.move_raw_ids.filtered(lambda m: m.state == 'draft'):
                    sub_name = mv.multilevel_kitting_name
                    if sub_name: #if its blank, location for this move stays the source_location for the MO
                        if sub_name in sublocation_dict:
                            sublocation_dict[sub_name].append(mv)
                        else:
                            sublocation_dict[sub_name] = [mv]
                
                for key in sublocation_dict:
                    sublocation_id = production.location_src_id.child_ids.filtered(lambda r: r.name == key)
                    if sublocation_id:
                        sublocation_id = sublocation_id[0]
                    else:
                        #Create Locations
                        loc = self.env['stock.location']
                        sublocation_id = loc.create({
                            'name': key,
                            'location_id': production.location_src_id.id
                        })
                        if production.location_src_id.barcode:
                            sublocation_id.barcode = production.location_src_id + '-' + key
                    for mv in sublocation_dict[key]:
                        mv.location_id = sublocation_id

    def write(self, vals):
        for production in self:
            if 'move_raw_ids' in vals and production.state != 'draft':
                production.create_and_set_sublocations()  

        res = super().write(vals)
        return res

    def action_confirm(self):
        for production in self:
            production.create_and_set_sublocations() 

        res = super().action_confirm()
        return res        

    def button_plan(self):
        orders_to_plan = self.filtered(lambda order: order.routing_id and order.state == 'confirmed')
        for order in orders_to_plan:
            order.create_and_set_sublocations() 

        res = super().button_plan()
        return res     

    def _get_move_raw_values(self, bom_line, line_data):
        data = super()._get_move_raw_values(bom_line, line_data)
        if self.bom_id and self.bom_id.multilevel_kitting:
            data['multilevel_kitting_name'] = bom_line.multilevel_kitting_name
        return data         

class MrpBom(models.Model):
    _inherit = "mrp.bom"
    multilevel_kitting = fields.Boolean('Multilevel BOM Kitting', default=True, help="If ticked, Manufacturing Order raw mateial locations reflect the multilevel BOM hierarchy")

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    multilevel_kitting_name = fields.Char('Bin Name', help="If multilevel kitting is enabled, this sublocation of the source will be used as the name of the raw material location for the related stock move")
    