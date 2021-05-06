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
            'group_propagation_option': 'none',
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
            'group_propagation_option': 'none',
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
            'group_propagation_option': 'none',
        })                            

        #Make Stores the default location for the default Receipt operation type
        self.warehouse.in_type_id.default_location_dest_id = self.Stores   

        #activate push_leftover option        
        self.warehouse.in_type_id.push_leftover = True          


        #Create products
        self.product = self.env['product.product']
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

        return result
    
    def test_unsplit(self):
        "Verify normal behaviour when the expected quantity matches"
        neededQty = 5.0
        orderedQty = 5.0

        #Create procurement
        values = {
            'warehouse_id': self.warehouse,
            'route_ids': self.ComponentResupply,
        }
        PG = self.env['procurement.group']
        strOrigin = 'push_leftover Test Replenishment'
        
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
        with self.assertRaises(exceptions.UserError):
            #Raises error becuase there's no rule to handle a need in goods in.  We'll do this manuall so we can make that move for a larger quanitty.
            PG.run([proc])
        
        myMoves = self.env['stock.move'].search([('origin', '=', strOrigin)])
        self.assertEqual(len(myMoves), 1, msg='There are not 3 moves generated')

        move1 = myMoves.search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.HUST.id)])
        self.assertEqual(len(move1), 1, msg='There are not 1 move from Goods In to HUST')

        #There are none to move right now, so quantity should be 0.
        self.assertEqual(move1.product_uom_qty, neededQty, msg='There are not %s units in GoodsIn->Hust' % neededQty)

        #create the equivalent of a buy move
        template = {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (''),
            'product_id': self.CompA.id,
            'product_uom': self.CompA.uom_id.id,
            'product_uom_qty': orderedQty,
            'location_id': self.ref('stock.stock_location_suppliers'),
            'location_dest_id': self.goodsIn.id,
            'move_dest_ids': [(6, 0, [move1.id])],
            'state': 'draft',
            'origin': strOrigin,
            'picking_type_id': self.warehouse.in_type_id.id,
        }
        manual_PO = self.env['stock.move'].create([template])
        manual_PO._action_confirm()
        manual_PO._action_assign()

        myMoves = self.env['stock.move'].search([('origin', '=', strOrigin)])
        self.assertEqual(len(myMoves), 2, msg='There are not 2 moves generated')

        move1 = myMoves.search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.HUST.id)])    
        move2 = myMoves.search([('location_dest_id', '=', self.goodsIn.id)])

        self.assertEqual(len(move1), 1, msg='There are not 1 move from Goods In to HUST')
        self.assertEqual(len(move2), 1, msg='There are not 1 move to Goods In')

        self.assertEqual(move1.product_uom_qty, neededQty, msg='There are not %s units in GoodsIn->Hust' % neededQty)
        self.assertEqual(move2.product_uom_qty, orderedQty, msg='There are not %s units in GoodsIn->Hust' % orderedQty)

    def test_split(self):
        "Verify move is split when the quantity exceeds the next in the chain"
        neededQty = 5.0
        orderedQty = 8.0

        #Create procurement
        values = {
            'warehouse_id': self.warehouse,
            'route_ids': self.ComponentResupply,
        }
        PG = self.env['procurement.group']
        strOrigin = 'push_leftover Test Replenishment'
        
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
        with self.assertRaises(exceptions.UserError):
            #Raises error becuase there's no rule to handle a need in goods in.  We'll do this manuall so we can make that move for a larger quanitty.
            PG.run([proc])
        
        myMoves = self.env['stock.move'].search([('origin', '=', strOrigin)])
        self.assertEqual(len(myMoves), 1, msg='There are not 3 moves generated')

        move1 = myMoves.search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.HUST.id)])
        self.assertEqual(len(move1), 1, msg='There are not 1 move from Goods In to HUST')

        #There are none to move right now, so quantity should be 0.
        self.assertEqual(move1.product_uom_qty, neededQty, msg='There are not %s units in GoodsIn->Hust' % neededQty)

        #create the equivalent of a buy move
        template = {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (''),
            'product_id': self.CompA.id,
            'product_uom': self.CompA.uom_id.id,
            'product_uom_qty': orderedQty,
            'location_id': self.ref('stock.stock_location_suppliers'),
            'location_dest_id': self.goodsIn.id,
            'move_dest_ids': [(6, 0, [move1.id])],
            'state': 'draft',
            'origin': strOrigin,
            'picking_type_id': self.warehouse.in_type_id.id,
        }
        manual_PO = self.env['stock.move'].create([template])
        manual_PO._action_confirm()
        manual_PO._action_assign()

        myMoves = self.env['stock.move'].search([('origin', '=', strOrigin)])
        self.assertEqual(len(myMoves), 3, msg='There are not 3 moves generated')

        move1 = myMoves.search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.HUST.id)])    
        move3 = myMoves.search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.Stores.id)])    

        self.assertEqual(len(move1), 1, msg='There are not 1 move from Goods In to HUST')
        self.assertEqual(len(move3), 1, msg='There are not 1 move from Goods In to Stores')

        self.assertEqual(move1.product_uom_qty, neededQty, msg='There are not %s units in GoodsIn->Hust' % neededQty)
        self.assertEqual(move3.product_uom_qty, (orderedQty - neededQty), msg='There are not %s units in vendor->GoodsIn' % (orderedQty - neededQty))

    def test_split_off(self):
        "Verify no split when the quanitty exceeeds the next in the chain but the flag is off on the operation type"
        neededQty = 5.0
        orderedQty = 8.0
        
        self.warehouse.in_type_id.push_leftover = False     

        #Create procurement
        values = {
            'warehouse_id': self.warehouse,
            'route_ids': self.ComponentResupply,
        }
        PG = self.env['procurement.group']
        strOrigin = 'push_leftover Test Replenishment'
        
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
        with self.assertRaises(exceptions.UserError):
            #Raises error becuase there's no rule to handle a need in goods in.  We'll do this manuall so we can make that move for a larger quanitty.
            PG.run([proc])
        
        myMoves = self.env['stock.move'].search([('origin', '=', strOrigin)])
        self.assertEqual(len(myMoves), 1, msg='There are not 3 moves generated')

        move1 = myMoves.search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.HUST.id)])
        self.assertEqual(len(move1), 1, msg='There are not 1 move from Goods In to HUST')

        #There are none to move right now, so quantity should be 0.
        self.assertEqual(move1.product_uom_qty, neededQty, msg='There are not %s units in GoodsIn->Hust' % neededQty)

        #create the equivalent of a buy move
        template = {
            'name': (''),
            'product_id': self.CompA.id,
            'product_uom': self.CompA.uom_id.id,
            'product_uom_qty': orderedQty,
            'location_id': self.ref('stock.stock_location_suppliers'),
            'location_dest_id': self.goodsIn.id,
            'move_dest_ids': [(6, 0, [move1.id])],
            'state': 'draft',
            'origin': strOrigin,
            'picking_type_id': self.warehouse.in_type_id.id,
        }
        manual_PO = self.env['stock.move'].create([template])
        manual_PO._action_confirm()
        manual_PO._action_assign()

        myMoves = self.env['stock.move'].search([('origin', '=', strOrigin)])
        self.assertEqual(len(myMoves), 2, msg='There are not 2 moves generated')

        move1 = myMoves.search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.HUST.id)])    
        move2 = myMoves.search([('location_dest_id', '=', self.goodsIn.id)])

        self.assertEqual(len(move1), 1, msg='There are not 1 move from Goods In to HUST')
        self.assertEqual(len(move2), 1, msg='There are not 1 move to Goods In')

        self.assertEqual(move1.product_uom_qty, neededQty, msg='There are not %s units in GoodsIn->Hust' % neededQty)
        self.assertEqual(move2.product_uom_qty, orderedQty, msg='There are not %s units ->GoodsIn' % orderedQty)
