from odoo.tests.common import SavepointCase

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
            'action': 'pull',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.Stores.id,
            'location_id': self.Builds.id,
            'procure_method': 'mts_else_alt',
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

        #create inventory
        self.inventoryCompA = self.env['stock.inventory'].create({
            'name': 'Starting CompA Inventory'   
        })      
        self.inventoryLineCompA = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_xid,
            'inventory_id': self.inventoryCompA.id,
            'product_qty': 2.0,
            'location_id': self.Vertical1.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()


        return result
    
    def test_create(self):
        "Trigger the restock rule in HUST"

        #create inventory
        self.inventoryNeed = self.env['stock.inventory'].create({
            'name': 'Fake manufacturing need'      
        })      
        self.inventoryLineNeed = self.env['stock.inventory.line'].create({
            'product_id': self.CompA.id,
            'product_uom_id': self.uom_xid,
            'inventory_id': self.inventoryNeed.id,
            'product_qty': -4.0,
            'location_id': self.HUST.id,
        })
        self.inventoryNeed._action_start()
        self.inventoryNeed.action_validate()   

        self.scheduler._procure_calculation_orderpoint()  #Once to trigger the pull from
        
        ##TODO: How do I test for the existence of two new stock moves???
        self.assertEqual(True, True)

