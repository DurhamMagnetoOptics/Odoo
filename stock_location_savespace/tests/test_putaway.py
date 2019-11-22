from odoo.tests.common import TransactionCase
from odoo import exceptions

class TestMove(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)

        self.warehouse = self.env.ref('stock.warehouse0')
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')

        #Create Locations
        self.Location = self.env['stock.location']
        self.goodsIn = self.Location.create({
            'name': 'Goods In',
            'location_id': self.warehouse.view_location_id.id
        })
        self.Builds = self.Location.create({
            'name': 'Builds',
            'location_id': self.warehouse.view_location_id.id
        })                                
        self.HUST = self.Location.create({
            'name': 'HUST',
            'location_id': self.Builds.id
        })        
        self.Stores = self.Location.create({
            'name': 'Stores',
            'location_id': self.warehouse.view_location_id.id
        })
        self.Vertical1 = self.Location.create({
            'name': 'Vertical 1',
            'location_id': self.Stores.id
        })        
        self.Vertical2 = self.Location.create({
            'name': 'Vertical 1',
            'location_id': self.Stores.id
        })    
        self.Shelf1 = self.Location.create({
            'name': 'Shelf 1',
            'location_id': self.Vertical1.id
        })        
        self.Shelf2 = self.Location.create({
            'name': 'Shelf 2',
            'location_id': self.Vertical1.id
        })         
        self.Shelf3 = self.Location.create({
            'name': 'Shelf 3',
            'location_id': self.Vertical2.id
        })        
        self.Shelf4 = self.Location.create({
            'name': 'Shelf 4',
            'location_id': self.Vertical2.id
        })  

        #Create product
        self.product = self.env['product.product']
        self.CompA = self.product.create({
            'name': 'CompA',
            'categ_id': self.ref('product.product_category_5'),
            'standard_price': 2.5,
            'list_price': 2.5,
            'type': 'product',
            'weight': 0.01,
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'description': 'Machined Component',
            'default_code': 'PL-12345',
        })                                  
        
        return result
    
    def test_null_putaway(self):
        "Verify normal behaviour if override disabled and putaway exists"

        #create putaway rule
        self.putawayCompA = self.env['stock.putaway.rule'].create({
            'product_id': self.CompA.id,
            'location_in_id': self.Stores.id,
            'location_out_id': self.Shelf2.id,            
        })          

        #Create stock move
        move1 = self.env['stock.move'].create({
            'name': 'savespace_test_putaway_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.Stores.id,
            'product_id': self.CompA.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state, 'confirmed')

        # assignment
        move1._action_assign()
        self.assertEqual(move1.state, 'assigned')
        self.assertEqual(len(move1.move_line_ids), 1)

        # check if the putaway was rightly applied
        self.assertEqual(move1.move_line_ids.location_dest_id.id, self.Shelf2.id)        

    def test_null_noputaway(self):
        "Verify normal behaviour if override disabled and no putaway exists"     

        #Create stock move
        move1 = self.env['stock.move'].create({
            'name': 'savespace_test_putaway_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.Stores.id,
            'product_id': self.CompA.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state, 'confirmed')

        # assignment
        move1._action_assign()
        self.assertEqual(move1.state, 'assigned')
        self.assertEqual(len(move1.move_line_ids), 1)

        # check if the putaway was rightly applied
        self.assertEqual(move1.move_line_ids.location_dest_id.id, self.Stores.id)          

    def test_putaway_nostock(self):
        "Verify behaviour if override enabled and putaway exists, but no stock"

        #Enable override
        self.Stores.putaway_savespace = True

        #create putaway rule
        self.putawayCompA = self.env['stock.putaway.rule'].create({
            'product_id': self.CompA.id,
            'location_in_id': self.Stores.id,
            'location_out_id': self.Shelf2.id,            
        })          

        #Create stock move
        move1 = self.env['stock.move'].create({
            'name': 'savespace_test_putaway_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.Stores.id,
            'product_id': self.CompA.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state, 'confirmed')

        # assignment
        move1._action_assign()
        self.assertEqual(move1.state, 'assigned')
        self.assertEqual(len(move1.move_line_ids), 1)

        # check if the putaway was rightly applied
        self.assertEqual(move1.move_line_ids.location_dest_id.id, self.Shelf2.id)    


    def test_noputaway_nostock(self):
        "Verify behaviour if override enabled and no putaway exists and no stock"     

        #Enable override
        self.Stores.putaway_savespace = True

        #Create stock move
        move1 = self.env['stock.move'].create({
            'name': 'savespace_test_putaway_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.Stores.id,
            'product_id': self.CompA.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state, 'confirmed')

        # assignment
        move1._action_assign()
        self.assertEqual(move1.state, 'assigned')
        self.assertEqual(len(move1.move_line_ids), 1)

        # check if the putaway was rightly applied
        self.assertEqual(move1.move_line_ids.location_dest_id.id, self.Stores.id)           

    def test_putaway_stock(self):
        "Verify behaviour if override enabled and putaway exists and so does stock"

        #Enable override
        self.Stores.putaway_savespace = True

        #create inventory
        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Starting CompA Inventory'
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_unit.id,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': 2.0,
            'location_id': self.Shelf4.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()          

        #create putaway rule
        self.putawayCompA = self.env['stock.putaway.rule'].create({
            'product_id': self.CompA.id,
            'location_in_id': self.Stores.id,
            'location_out_id': self.Shelf2.id,            
        })          

        #Create stock move
        move1 = self.env['stock.move'].create({
            'name': 'savespace_test_putaway_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.Stores.id,
            'product_id': self.CompA.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state, 'confirmed')

        # assignment
        move1._action_assign()
        self.assertEqual(move1.state, 'assigned')
        self.assertEqual(len(move1.move_line_ids), 1)

        # check if the putaway was rightly applied
        self.assertEqual(move1.move_line_ids.location_dest_id.id, self.Shelf2.id)    


    def test_noputaway_stock_elsewhere(self):
        "Verify behaviour if override enabled and no putaway exists but stock exists in a non-child location"   

        #Enable override
        self.Stores.putaway_savespace = True

        #create inventory
        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Starting CompA Inventory'
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_unit.id,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': 2.0,
            'location_id': self.HUST.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()            

        #Create stock move
        move1 = self.env['stock.move'].create({
            'name': 'savespace_test_putaway_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.Stores.id,
            'product_id': self.CompA.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state, 'confirmed')

        # assignment
        move1._action_assign()
        self.assertEqual(move1.state, 'assigned')
        self.assertEqual(len(move1.move_line_ids), 1)

        # check if the putaway was rightly applied
        self.assertEqual(move1.move_line_ids.location_dest_id.id, self.Stores.id)       


    def test_putaway_stock(self):
        "Verify behaviour if override enabled and putaway exists and so does stock"

        #Enable override
        self.Stores.putaway_savespace = True

        #create inventory
        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Starting CompA Inventory'
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_unit.id,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': 2.0,
            'location_id': self.Shelf4.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()          

        #create putaway rule
        self.putawayCompA = self.env['stock.putaway.rule'].create({
            'product_id': self.CompA.id,
            'location_in_id': self.Stores.id,
            'location_out_id': self.Shelf2.id,            
        })          

        #Create stock move
        move1 = self.env['stock.move'].create({
            'name': 'savespace_test_putaway_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.Stores.id,
            'product_id': self.CompA.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state, 'confirmed')

        # assignment
        move1._action_assign()
        self.assertEqual(move1.state, 'assigned')
        self.assertEqual(len(move1.move_line_ids), 1)

        # check if the putaway was rightly applied
        self.assertEqual(move1.move_line_ids.location_dest_id.id, self.Shelf2.id)    


    def test_noputaway_stock(self):
        "Verify behaviour if override enabled and no putaway exists but stock exists"   

        #Enable override
        self.Stores.putaway_savespace = True

        #create inventory
        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Starting CompA Inventory'
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_unit.id,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': 2.0,
            'location_id': self.Shelf4.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()            

        #Create stock move
        move1 = self.env['stock.move'].create({
            'name': 'savespace_test_putaway_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.Stores.id,
            'product_id': self.CompA.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state, 'confirmed')

        # assignment
        move1._action_assign()
        self.assertEqual(move1.state, 'assigned')
        self.assertEqual(len(move1.move_line_ids), 1)

        # check if the putaway was rightly applied
        ##TODO: should be Shelf4 when things are working
        self.assertEqual(move1.move_line_ids.location_dest_id.id, self.Shelf4.id)              
                 
    def test_putaway_stock(self):
        "Verify behaviour if override enabled and putaway exists and so does stock"

        #Enable override
        self.Stores.putaway_savespace = True

        #create inventory
        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Starting CompA Inventory'
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_unit.id,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': 2.0,
            'location_id': self.Shelf4.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()          

        #create putaway rule
        self.putawayCompA = self.env['stock.putaway.rule'].create({
            'product_id': self.CompA.id,
            'location_in_id': self.Stores.id,
            'location_out_id': self.Shelf2.id,            
        })          

        #Create stock move
        move1 = self.env['stock.move'].create({
            'name': 'savespace_test_putaway_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.Stores.id,
            'product_id': self.CompA.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state, 'confirmed')

        # assignment
        move1._action_assign()
        self.assertEqual(move1.state, 'assigned')
        self.assertEqual(len(move1.move_line_ids), 1)

        # check if the putaway was rightly applied
        self.assertEqual(move1.move_line_ids.location_dest_id.id, self.Shelf2.id)    


    def test_noputaway_stock_newer(self):
        "Verify behaviour if override enabled and no putaway exists but stock exists"   

        #Enable override
        self.Stores.putaway_savespace = True

        #create inventory
        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Starting CompA Inventory'
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_unit.id,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': 2.0,
            'location_id': self.Shelf4.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()            

        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Second CompA Inventory'
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_unit.id,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': 3.0,
            'location_id': self.Shelf3.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()           

        #Create stock move
        move1 = self.env['stock.move'].create({
            'name': 'savespace_test_putaway_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.Stores.id,
            'product_id': self.CompA.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state, 'confirmed')

        # assignment
        move1._action_assign()
        self.assertEqual(move1.state, 'assigned')
        self.assertEqual(len(move1.move_line_ids), 1)

        # check if the putaway was rightly applied
        ##TODO: should be Shelf4 when things are working
        self.assertEqual(move1.move_line_ids.location_dest_id.id, self.Shelf3.id)   

    def test_null_noputaway_stock_newer(self):
        "Verify behaviour if override enabled and no putaway exists but stock exists"   

        #create inventory
        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Starting CompA Inventory'
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_unit.id,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': 2.0,
            'location_id': self.Shelf4.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()            

        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Second CompA Inventory'
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_unit.id,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': 3.0,
            'location_id': self.Shelf3.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()           

        #Create stock move
        move1 = self.env['stock.move'].create({
            'name': 'savespace_test_putaway_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.Stores.id,
            'product_id': self.CompA.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 100.0,
        })
        move1._action_confirm()
        self.assertEqual(move1.state, 'confirmed')

        # assignment
        move1._action_assign()
        self.assertEqual(move1.state, 'assigned')
        self.assertEqual(len(move1.move_line_ids), 1)

        # check if the putaway was rightly applied
        ##TODO: should be Shelf4 when things are working
        self.assertEqual(move1.move_line_ids.location_dest_id.id, self.Stores.id)           
