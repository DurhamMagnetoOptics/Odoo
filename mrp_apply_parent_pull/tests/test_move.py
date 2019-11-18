from odoo.tests.common import SavepointCase

class TestMove(SavepointCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)

        self.warehouse = self.env.ref('stock.warehouse0')
        self.uom_xid = self.ref('uom.product_uom_unit')

        #Create Locations
        self.Location = self.env['stock.location']
        self.goodsIn = self.Location.create({
            'name': 'Goods In',
            'location_id': self.warehouse.view_location_id.id
        })
        self.Stores = self.Location.create({
            'name': 'Stores',
            'location_id': self.warehouse.view_location_id.id
        })
        self.Vertical1 = self.Location.create({
            'name': 'Vertical 1',
            'location_id': self.Stores.id
        })
        self.Builds = self.Location.create({
            'name': 'Builds',
            'location_id': self.warehouse.view_location_id.id
        })                                
        self.HUST = self.Location.create({
            'name': 'HUST',
            'location_id': self.Builds.id
        })        
  

        #Make Stores the default location for the default Receipt operation type
        self.warehouse.in_type_id.default_location_dest_id = self.Stores             

        #Create route
        self.route = self.env['stock.location.route']
        self.rule = self.env['stock.rule']
        self.ComponentResupply = self.route.create({
            'name': 'Component Resupply',
            'product_selectable': True
        })            


        #Create products
        self.product = self.env['product.product']
        self.MW3 = self.product.create({
            'name': 'MW3',
            'categ_id': self.ref('product.product_category_5'),
            'standard_price': 290.0,
            'list_price': 520.0,
            'type': 'product',
            'weight': 0.01,
            'uom_id': self.uom_xid,
            'uom_po_id': self.uom_xid,
            'description': 'MicroWriter 3',
            'default_code': 'DMO_MW3',
        })
        self.CompA = self.product.create({
            'name': 'CompA',
            'categ_id': self.ref('product.product_category_5'),
            'standard_price': 2.5,
            'list_price': 2.5,
            'type': 'product',
            'weight': 0.01,
            'uom_id': self.uom_xid,
            'uom_po_id': self.uom_xid,
            'description': 'Machined Component',
            'default_code': 'PL-12345',
            'route_ids': [(6,0,[self.ComponentResupply.id])],
        })       

        #Create Rules
        self.ResupplyInPlace = self.rule.create({
            'name': 'Resupply In Place',
            'action': 'pull',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.goodsIn.id,
            'location_id': self.Builds.id,
            'procure_method': 'make_to_order',
            'route_id': self.ComponentResupply.id,
            'sequence': 10,
        })
        self.ResupplyStores = self.rule.create({
            'name': 'Resupply Stores',
            'action': 'pull',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.goodsIn.id,
            'location_id': self.Stores.id,
            'procure_method': 'make_to_order',
            'route_id': self.ComponentResupply.id,
            'sequence': 15,
        })    
        self.PutawayLeftovers = self.rule.create({
            'name': 'Putaway Leftovers',
            'action': 'push',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.goodsIn.id,
            'location_id': self.Stores.id,
            'auto': 'manual',
            'route_id': self.ComponentResupply.id,
            'sequence': 20,
        })       
        self.TriggerPO = self.rule.create({
            'name': 'Trigger PO',
            'action': 'pull',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.ref('stock.stock_location_suppliers'),
            'location_id': self.goodsIn.id,
            'procure_method': 'make_to_stock',
            'route_id': self.ComponentResupply.id,
            'sequence': 25,
        })   
        self.MTOKitting = self.rule.create({
            'name': 'Kit On Demand',
            'action': 'pull',
            'picking_type_id': self.warehouse.manu_type_id.id,
            'location_src_id': self.Builds.id,
            'location_id': self.CompA.property_stock_production.id,
            'procure_method': 'make_to_order',
            'route_id': self.ComponentResupply.id,
            'sequence': 30,
        })          
          


        #Create BOM
        self.MW3_BOM = self.env['mrp.bom'].create({
            'product_tmpl_id': self.MW3.product_tmpl_id.id,
            'product_uom_id': self.ref('uom.product_uom_unit')
        })
        self.compA_BOM_line = self.env['mrp.bom.line'].create({
            'product_id': self.CompA.id,
            'product_qty': 5.0,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'sequence': 5,
            'bom_id': self.MW3_BOM.id
        })   


        #create Suplier
        self.supplierCompA = self.env['product.supplierinfo'].create({
            'product_tmpl_id': self.CompA.product_tmpl_id.id,
            'name': self.ref('base.res_partner_12'),
            'delay': 1,
            'min_qty': 0.0,
            'price': 2.50,
        })

        #create reordering rule
        self.orderpointCompA = self.env['stock.warehouse.orderpoint'].create({
            'product_id': self.CompA.id,
            'location_id': self.HUST.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 1.0,
        })        

        #create putaway rule
        self.putawayCompA = self.env['stock.putaway.rule'].create({
            'product_id': self.CompA.id,
            'location_in_id': self.Stores.id,
            'location_out_id': self.Vertical1.id,            
        })         


        return result
    
    def test_parent_pull(self):
        "Creat an MO with an MTO route on the parent location"
        self.MTOKitting.procure_method = 'make_to_order'

        #create MO
        strOrigin = 'mts_else_mto Test Replenishment'
        self.MW3_MO = self.env['mrp.production'].create({
            'name': strOrigin,
            'origin': strOrigin,
            'product_tmpl_id': self.MW3.product_tmpl_id.id,
            'product_id': self.MW3.id,
            'product_qty': 1.0,
            'location_src_id': self.HUST.id,
            'location_dest_id': self.HUST.id,
            'bom_id': self.MW3_BOM.id,
            'product_uom_id': self.ref('uom.product_uom_unit')
        })      
        self.MW3_MO._onchange_move_raw()
        self.MW3_MO.action_confirm()
        
        myMoves = self.env['stock.move'].search([('origin', '=', strOrigin)])
        move1 = myMoves.search([('location_id', '=', self.CompA.property_stock_production.id), ('location_dest_id', '=', self.HUST.id)])
        move2 = myMoves.search([('location_id', '=', self.HUST.id), ('location_dest_id', '=', self.CompA.property_stock_production.id)])
        move3 = myMoves.search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.HUST.id)])
        move4 = myMoves.search([('location_dest_id', '=', self.goodsIn.id)])

        self.assertEqual(len(myMoves), 4, msg='More than 4 moves generated')
        self.assertEqual(len(move1), 1, msg='More than 1 move prod->HUST')
        self.assertEqual(len(move2), 1, msg='More than 1 move HUST->prod')
        self.assertEqual(len(move3), 1, msg='More than 1 move GoodsIn->HUST')
        self.assertEqual(len(move4), 1, msg='More than 1 move to GoodsIn')


    def test_no_parent_pull(self):
        "Creat an MO with an MTO route on the parent location"
        self.MTOKitting.procure_method = 'make_to_stock'

        #create MO
        strOrigin = 'mts_else_mto Test Replenishment'
        self.MW3_MO = self.env['mrp.production'].create({
            'name': strOrigin,
            'origin': strOrigin,
            'product_tmpl_id': self.MW3.product_tmpl_id.id,
            'product_id': self.MW3.id,
            'product_qty': 1.0,
            'location_src_id': self.HUST.id,
            'location_dest_id': self.HUST.id,
            'bom_id': self.MW3_BOM.id,
            'product_uom_id': self.ref('uom.product_uom_unit')
        })      
        self.MW3_MO._onchange_move_raw()
        self.MW3_MO.action_confirm()
        
        myMoves = self.env['stock.move'].search([('origin', '=', strOrigin)])
        move1 = myMoves.search([('location_id', '=', self.CompA.property_stock_production.id), ('location_dest_id', '=', self.HUST.id)])
        move2 = myMoves.search([('location_id', '=', self.HUST.id), ('location_dest_id', '=', self.CompA.property_stock_production.id)])
        self.assertEqual(len(myMoves), 2, msg='More than 2 moves generated')        
        self.assertEqual(len(move1), 1, msg='More than 1 move prod->HUST')    
        self.assertEqual(len(move2), 1, msg='More than 1 move HUST->prod')          
