from odoo.tests.common import SavepointCase
from odoo import exceptions

class TestMove(SavepointCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)

        self.scheduler = self.env['stock.scheduler.compute']
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

        #Create route
        self.route = self.env['stock.location.route']
        self.rule = self.env['stock.rule']
        self.ComponentResupply = self.route.create({
            'name': 'Component Resupply',
            'product_selectable': True
        })
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
        self.KitFromStores = self.rule.create({
            'name': 'Kit From Stores',
            'action': 'branch',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.Stores.id,
            'location_id': self.Builds.id,
            'procure_method': 'make_to_stock',
            'alternate_rule_id': self.ResupplyInPlace.id,            
            'route_id': self.ComponentResupply.id,
            'sequence': 5,
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

        #Make Stores the default location for the default Receipt operation type
        self.warehouse.in_type_id.default_location_dest_id = self.Stores             


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
    
    def test_split(self):
        "Trigger the restock with some but not enough"

        #create inventory
        #self.inventoryNeed = self.env['stock.inventory'].create({
        #    'name': 'Fake manufacturing need'      
        #})      
        #self.inventoryLineNeed = self.env['stock.inventory.line'].create({
        #    'product_id': self.CompA.id,
        #    'product_uom_id': self.uom_xid,
        #    'inventory_id': self.inventoryNeed.id,
        #    'product_qty': -4.0,
        #    'location_id': self.HUST.id,
        #})
        #self.inventoryNeed._action_start()
        #self.inventoryNeed.action_validate()   
        #self.scheduler._procure_calculation_orderpoint()  #Once to trigger the pull from """

        inStockQty =  2.0
        neededQty = 5.0

        #create inventory
        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Starting CompA Inventory'   
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_xid,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': inStockQty,
            'location_id': self.Vertical1.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()


        #Create procurement
        values = {
            'warehouse_id': self.warehouse,
            'route_ids': self.ComponentResupply,
        }
        PG = self.env['procurement.group']
        strOrigin = 'mts_else_mto Test Replenishment'
        
        proc = PG.Procurement(
            self.CompA,
            neededQty,
            self.CompA.uom_id,
            self.HUST,  # Location
            "Test Replenishment",  # Name
            strOrigin,  # Origin
            self.warehouse.company_id,
            values  # Values
        )
        PG.run([proc])
        
        myMoves = self.env['stock.move'].search([('origin', '=', strOrigin)])
        move1 = myMoves.search([('location_id', '=', self.Stores.id), ('location_dest_id', '=', self.HUST.id)])
        move2 = myMoves.search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.HUST.id)])
        move3 = myMoves.search([('location_dest_id', '=', self.goodsIn.id)])

        self.assertEqual(len(myMoves), 3, msg='More than 3 moves generated')
        self.assertEqual(len(move1), 1, msg='More than 1 move from Stores to HUST')
        self.assertEqual(len(move2), 1, msg='More than 1 move from Goods In to HUST')
        self.assertEqual(len(move3), 1, msg='More than 1 move to Goods In')

        self.assertEqual(move1.product_qty, inStockQty, msg='More than %s units in Stores->Hust' % inStockQty)
        self.assertEqual(move2.product_qty, neededQty - inStockQty, msg='More than %s units in GoodsIn->Hust' % (neededQty - inStockQty))
        self.assertEqual(move3.product_qty, neededQty - inStockQty, msg='More than %s units in Vendors->GoodsIn' % (neededQty - inStockQty))

    def test_allstock(self):
        "Trigger the restock with more than enough"

        inStockQty =  8.0
        neededQty = 5.0

        #create inventory
        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Starting CompA Inventory'   
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_xid,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': inStockQty,
            'location_id': self.Vertical1.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()


        #Create procurement
        values = {
            'warehouse_id': self.warehouse,
            'route_ids': self.ComponentResupply,
        }
        PG = self.env['procurement.group']
        strOrigin = 'mts_else_mto Test Replenishment'
        
        proc = PG.Procurement(
            self.CompA,
            neededQty,
            self.CompA.uom_id,
            self.HUST,  # Location
            "Test Replenishment",  # Name
            strOrigin,  # Origin
            self.warehouse.company_id,
            values  # Values
        )
        PG.run([proc])
        
        myMoves = self.env['stock.move'].search([('origin', '=', strOrigin)])
        move1 = myMoves.search([('location_id', '=', self.Stores.id), ('location_dest_id', '=', self.HUST.id)])
        #move2 = myMoves.search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.HUST.id)])
        #move3 = myMoves.search([('location_dest_id', '=', self.goodsIn.id)])

        self.assertEqual(len(myMoves), 1, msg='More than 3 moves generated')
        self.assertEqual(len(move1), 1, msg='More than 1 move from Stores to HUST')
        #self.assertEqual(len(move2), 1, msg='More than 1 move from Goods In to HUST')
        #self.assertEqual(len(move3), 1, msg='More than 1 move to Goods In')

        self.assertEqual(move1.product_qty, neededQty, msg='More than %s units in Stores->Hust' % neededQty)
        #self.assertEqual(move2.product_qty, neededQty - inStockQty, msg='More than %s units in GoodsIn->Hust' % (neededQty - inStockQty))
        #self.assertEqual(move3.product_qty, neededQty - inStockQty, msg='More than %s units in Vendors->GoodsIn' % (neededQty - inStockQty))        


    def test_nostock(self):
        "Trigger the restock with more than enough"

        inStockQty =  0.0
        neededQty = 5.0

        #create inventory
        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Starting CompA Inventory'   
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_xid,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': inStockQty,
            'location_id': self.Vertical1.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()


        #Create procurement
        values = {
            'warehouse_id': self.warehouse,
            'route_ids': self.ComponentResupply,
        }
        PG = self.env['procurement.group']
        strOrigin = 'mts_else_mto Test Replenishment'
        
        proc = PG.Procurement(
            self.CompA,
            neededQty,
            self.CompA.uom_id,
            self.HUST,  # Location
            "Test Replenishment",  # Name
            strOrigin,  # Origin
            self.warehouse.company_id,
            values  # Values
        )
        PG.run([proc])
        
        myMoves = self.env['stock.move'].search([('origin', '=', strOrigin)])
        #move1 = myMoves.search([('location_id', '=', self.Stores.id), ('location_dest_id', '=', self.HUST.id)])
        move2 = myMoves.search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.HUST.id)])
        move3 = myMoves.search([('location_dest_id', '=', self.goodsIn.id)])

        self.assertEqual(len(myMoves), 2, msg='More than 3 moves generated')
        #self.assertEqual(len(move1), 1, msg='More than 1 move from Stores to HUST')
        self.assertEqual(len(move2), 1, msg='More than 1 move from Goods In to HUST')
        self.assertEqual(len(move3), 1, msg='More than 1 move to Goods In')

        #self.assertEqual(move1.product_qty, neededQty, msg='More than %s units in Stores->Hust' % neededQty)
        self.assertEqual(move2.product_qty, neededQty, msg='More than %s units in GoodsIn->Hust' % neededQty)
        self.assertEqual(move3.product_qty, neededQty, msg='More than %s units in Vendors->GoodsIn' % neededQty)

    def test_location(self):
        alt_rule = self.rule.create({
            'name': 'Resupply In Place',
            'action': 'pull',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.goodsIn.id,
            'location_id': self.goodsIn.id,
            'procure_method': 'make_to_order',
            'route_id': self.ComponentResupply.id,
            'sequence': 10,
        })
        prime_vals = {
            'name': 'Kit From Stores',
            'action': 'branch',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.Stores.id,
            'location_id': self.Builds.id,
            'procure_method': 'make_to_stock',
            'alternate_rule_id': alt_rule.id,            
            'route_id': self.ComponentResupply.id,
            'sequence': 5,
        }

        with self.assertRaises(exceptions.ValidationError):
            #Raises error becuase alternate rule and primary rule must have the same destination
            prime_rule = self.rule.create(prime_vals)                    


    def test_location_src(self):        
        alt_rule = self.rule.create({
            'name': 'Resupply In Place',
            'action': 'pull',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.Builds.id,
            'location_id': self.Builds.id,
            'procure_method': 'make_to_order',
            'route_id': self.ComponentResupply.id,
            'sequence': 10,
        })
        prime_vals = {
            'name': 'Kit From Stores',
            'action': 'branch',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.Stores.id,
            'location_id': self.Builds.id,
            'procure_method': 'make_to_stock',
            'alternate_rule_id': alt_rule.id,            
            'route_id': self.ComponentResupply.id,
            'sequence': 5,
        }
        with self.assertRaises(exceptions.ValidationError):
            #Raises error becuase alternate rule's source can't be primary rule's destination
            prime_rule = self.rule.create(prime_vals)                        
 

    def test_mtselsemto(self):        
        alt_rule = self.rule.create({
            'name': 'Resupply In Place',
            'action': 'pull',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.goodsIn.id,
            'location_id': self.Builds.id,
            'procure_method': 'make_to_order',
            'route_id': self.ComponentResupply.id,
            'sequence': 10,
        })
        prime_vals = {
            'name': 'Kit From Stores',
            'action': 'branch',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.Stores.id,
            'location_id': self.Builds.id,
            'procure_method': 'mts_else_mto',
            'alternate_rule_id': alt_rule.id,            
            'route_id': self.ComponentResupply.id,
            'sequence': 5,
        }
        with self.assertRaises(exceptions.ValidationError):
            #Raises error because we can't combine branch with mts_else_mto procurement
            prime_rule = self.rule.create(prime_vals)                