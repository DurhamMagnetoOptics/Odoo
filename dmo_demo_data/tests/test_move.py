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
            'location_id': self.warehouse.view_location_id.id,
            'putaway_savespace': True
        })
        self.Vertical1 = self.Location.create({
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
        self.Vertical2 = self.Location.create({
            'name': 'Vertical 2',
            'location_id': self.Stores.id
        })        
        self.Shelf3 = self.Location.create({
            'name': 'Shelf 3',
            'location_id': self.Vertical1.id
        })
        self.Shelf4 = self.Location.create({
            'name': 'Shelf 4',
            'location_id': self.Vertical1.id
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
        self.warehouse.in_type_id.default_location_dest_id = self.goodsIn             

        #Create route
        self.route = self.env['stock.location.route']
        self.rule = self.env['stock.rule']
        self.ComponentResupply = self.route.create({
            'name': 'Component Resupply',
            'product_selectable': True
        })      
        self.SubResupply = self.route.create({
            'name': 'Subassy Resupply',
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
            'sale_ok': True,
            'purchase_ok': False,
        })
        self.SubA = self.product.create({
            'name': 'SubA',
            'categ_id': self.ref('product.product_category_5'),
            'standard_price': 290.0,
            'list_price': 520.0,
            'type': 'product',
            'weight': 0.01,
            'uom_id': self.uom_xid,
            'uom_po_id': self.uom_xid,
            'description': 'Subassembly A',
            'default_code': 'DMO_XY2',
            'sale_ok': False,
            'purchase_ok': False,    
            'route_ids': [(6,0,[self.SubResupply.id])],
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
            'sale_ok': False,
            'purchase_ok': True,            
        })    
        self.CompB = self.product.create({
            'name': 'CompB',
            'categ_id': self.ref('product.product_category_5'),
            'standard_price': 2.5,
            'list_price': 2.5,
            'type': 'product',
            'weight': 0.01,
            'uom_id': self.uom_xid,
            'uom_po_id': self.uom_xid,
            'description': 'Screw',
            'default_code': 'PT-12345',
            'route_ids': [(6,0,[self.ComponentResupply.id])],
            'sale_ok': False,
            'purchase_ok': True,            
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
            'propagate_cancel': True,
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
            'propagate_cancel': True,
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
            'action': 'buy',
            'picking_type_id': self.warehouse.in_type_id.id,
            'location_id': self.goodsIn.id,
            'route_id': self.ComponentResupply.id,
            'sequence': 25,
            'group_propagation_option': 'none',
            'propagate_cancel': True,
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
            'propagate_cancel': True,
        })         


        self.MTOSubAssy = self.rule.create({
            'name': 'Build Subassy',
            'action': 'manufacture',
            'picking_type_id': self.warehouse.manu_type_id.id,
            'location_id': self.Builds.id,
            'route_id': self.SubResupply.id,
            'sequence': 25,
            'propagate_cancel': True,
        })   
        self.SubFromStores = self.rule.create({
            'name': 'Subs from Stores',
            'action': 'branch',
            'picking_type_id': self.warehouse.int_type_id.id,
            'location_src_id': self.Stores.id,
            'location_id': self.Builds.id,
            'procure_method': 'make_to_stock',
            'alternate_rule_id': self.MTOSubAssy.id,
            'route_id': self.SubResupply.id,
            'sequence': 20,
            'propagate_cancel': True,
        })    
        self.MTOKittingSub = self.rule.create({
            'name': 'Subassy On Demand',
            'action': 'pull',
            'picking_type_id': self.warehouse.manu_type_id.id,
            'location_src_id': self.Builds.id,
            'location_id': self.CompA.property_stock_production.id,
            'procure_method': 'make_to_order',
            'route_id': self.SubResupply.id,
            'sequence': 30,
            'propagate_cancel': True,
        })                    
          


        #Create BOM
        self.MW3_BOM = self.env['mrp.bom'].create({
            'product_tmpl_id': self.MW3.product_tmpl_id.id,
            'product_uom_id': self.ref('uom.product_uom_unit')
        })
        self.compA_BOM_line = self.env['mrp.bom.line'].create({
            'product_id': self.CompA.id,
            'product_qty': 25.0,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'sequence': 5,
            'bom_id': self.MW3_BOM.id
        })   
        self.SubA_BOM_line = self.env['mrp.bom.line'].create({
            'product_id': self.SubA.id,
            'product_qty': 2.0,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'sequence': 5,
            'bom_id': self.MW3_BOM.id
        })     

        self.SubA_BOM = self.env['mrp.bom'].create({
            'product_tmpl_id': self.SubA.product_tmpl_id.id,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'multilevel_kitting_name': 'XY2'
        })
        self.compA_subABOM_line = self.env['mrp.bom.line'].create({
            'product_id': self.CompA.id,
            'product_qty': 1.0,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'sequence': 5,
            'bom_id': self.SubA_BOM.id
        })   
        self.compB_subABOM_line = self.env['mrp.bom.line'].create({
            'product_id': self.CompB.id,
            'product_qty': 14.0,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'sequence': 5,
            'bom_id': self.SubA_BOM.id
        })              


        #create Suplier
        self.supplierCompA = self.env['product.supplierinfo'].create({
            'product_tmpl_id': self.CompA.product_tmpl_id.id,
            'name': self.ref('base.res_partner_12'),
            'delay': 1,
            'min_qty': 10.0,
            'increment_qty': 5.0,
            'round_up': True,
            'price': 2.50,
        })
        self.supplierCompB = self.env['product.supplierinfo'].create({
            'product_tmpl_id': self.CompB.product_tmpl_id.id,
            'name': self.ref('base.res_partner_12'),
            'delay': 1,
            'min_qty': 100.0,
            'increment_qty': 100.0,
            'round_up': True,
            'price': 2.50,
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
            'location_id': self.Shelf1.id,
        })
        self.inventoryCompA._action_start()
        self.inventoryCompA.action_validate()   

        self.inventorySubA = self.env['stock.inventory'].create({
            'name': 'Starting SubA Inventory'
        })      
        self.inventoryLineSubA = self.env['stock.inventory.line'].create({
            'product_id': self.SubA.id,
            'product_uom_id': self.uom_xid,
            'inventory_id': self.inventorySubA.id,
            'product_qty': 1.0,
            'location_id': self.Shelf4.id,
        })
        self.inventorySubA._action_start()
        self.inventorySubA.action_validate()         

        #activate push_leftover option on Receipt operation       
        self.warehouse.in_type_id.push_leftover = True  

        #Active apply_parent_pull on Manufacture operation
        self.warehouse.manu_type_id.apply_parent_pull = True
        self.warehouse.manu_type_id.multilevel_kitting = True
        self.warehouse.manu_type_id.default_location_dest_id = False
        self.warehouse.manu_type_id.default_location_src_id = False


        #Confirm any existing RFQs for the supplier of interest, so we don't muddy up our test results.
        myPOs = self.env['purchase.order'].search([('partner_id', '=', self.supplierCompA.name.id),('state', '=', 'draft')])
        for PO in myPOs:
            PO.button_confirm()

        return result
    
    def test_complete_flow(self):
        "Test MO -> PO flow, including partial stock, parent pull rule, leftover putaway, and MOQ rounding"

        #create MO
        strOrigin = 'DMO Demo Test Replenishment'
        self.MW3_MO_for2 = self.env['mrp.production'].create({
            'name': strOrigin + ' 1',
            'origin': strOrigin + ' 1',
            'product_tmpl_id': self.MW3.product_tmpl_id.id,
            'product_id': self.MW3.id,
            'product_qty': 2.0,
            'location_src_id': self.HUST.id,
            'location_dest_id': self.HUST.id,
            'bom_id': self.MW3_BOM.id,
            'product_uom_id': self.ref('uom.product_uom_unit')
        })      
       

        self.MW3_MO_for2._onchange_move_raw()
        self.MW3_MO_for2.action_confirm()

        #From setup function, above
        #in stock compA: 2
        #compA per MW3: 25.0
        #subA per MW3: 2.0
        #compA per subA: 1.0
        #compB per subA: 14.0
        #compA bought in 10 + 5's
        #compB bought in 100 + 100's

        ##Check MO
        myMOs = self.env['mrp.production'].search([('product_id', '=', self.SubA.id)])
        self.assertEqual(len(myMOs), 1, msg='Not 1 MO generated')
        self.assertEqual(myMOs.product_qty, 3.0)  #MO for need (4) less the one in stock, as per stock_mts_else_alt; created immediately (MTO) from rule on Builds (not Builds/HUST) as per mrp_apply_parent_pull

        ##Check PO
        myPOs = self.env['purchase.order'].search([('partner_id', '=', self.supplierCompA.name.id),('state', '=', 'draft')])
        self.assertEqual(len(myPOs), 1, msg='Not 1 PO generated')
        self.assertEqual(len(myPOs.order_line), 2, msg='Not 2 lines on the PO')
        compAline = myPOs.order_line.search([('product_id', '=', self.CompA.id)])
        compBline = myPOs.order_line.search([('product_id', '=', self.CompB.id)])
        self.assertEqual(len(compAline), 1, msg='Not 1 line for compA')
        self.assertEqual(len(compBline), 1, msg='Not 1 line for compB')
        #POs for need less in stock (as per stock_mts_else_alt) rounded up to min + N * inc as per product_supplierinfo_round_up
        self.assertEqual(compAline.desired_qty, 51.0, msg='More than %s items purchased' % 51.0)  #2*25 + (2*2-1)*1 - 2
        self.assertEqual(compAline.product_qty, 55.0, msg='More than %s items purchased' % 55.0)
        self.assertEqual(compBline.desired_qty, 42.0, msg='More than %s items purchased' % 42.0)  #(2*2-1)*14
        self.assertEqual(compBline.product_qty, 100.0, msg='More than %s items purchased' % 100.0)     

        #find XY2, created as per mrp_multilevel_kitting
        XY2 = False
        for loc in self.HUST.child_ids:
            if loc.name == self.SubA_BOM.multilevel_kitting_name:
                XY2 = loc
                continue
        self.assertTrue(loc)           
        
        """ Not ready to worry about mergings, yet
        self.MW3_MO_for4 = self.env['mrp.production'].create({
            'name': strOrigin + ' 2',
            'origin': strOrigin + ' 2',
            'product_tmpl_id': self.MW3.product_tmpl_id.id,
            'product_id': self.MW3.id,
            'product_qty': 4.0,
            'location_src_id': self.HUST.id,
            'location_dest_id': self.HUST.id,
            'bom_id': self.MW3_BOM.id,
            'product_uom_id': self.ref('uom.product_uom_unit')
        })             
        self.MW3_MO_for4._onchange_move_raw()
        self.MW3_MO_for4.action_confirm()

        ##Check PO again
        myPOs = self.env['purchase.order'].search([('partner_id', '=', self.supplierCompA.name.id),('state', '=', 'draft')])
        self.assertEqual(len(myPOs), 1, msg='Not 1 PO generated')
        self.assertEqual(len(myPOs.order_line), 2, msg='Not 2 lines on the PO')
        compAline = myPOs.order_line.search([('product_id', '=', self.CompA.id)])
        compBline = myPOs.order_line.search([('product_id', '=', self.CompB.id)])
        self.assertEqual(len(compAline), 1, msg='Not 1 line for compA')
        self.assertEqual(len(compBline), 1, msg='Not 1 line for compB')
        self.assertEqual(compAline.desired_qty, 159.0, msg='More than %s items purchased' % 159.0)  #2*25 + ((2*2)-1)*1 - 2 + 4*25 + 4*2*1
        self.assertEqual(compAline.product_qty, 160.0, msg='More than %s items purchased' % 160.0)
        self.assertEqual(compBline.desired_qty, 154.0, msg='More than %s items purchased' % 154.0)  #(2*2-1)*14 + 4*2*14
        self.assertEqual(compBline.product_qty, 200.0, msg='More than %s items purchased' % 200.0)    
        """

        #Place order
        myPOs.button_confirm()     
        
        #Check stock moves
        receipt_compA = self.env['stock.move'].search([('location_dest_id', '=', self.goodsIn.id),('product_id', '=', self.CompA.id)])
        receipt_compB = self.env['stock.move'].search([('location_dest_id', '=', self.goodsIn.id),('product_id', '=', self.CompB.id)])
        #stock moves created on demand (MTO) from pull rule in Builds (not Builds/HUST or Builds/HUST/XY2) as per mrp_apply_parent_pull
        compA_GItoHUST = self.env['stock.move'].search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.HUST.id),('product_id', '=', self.CompA.id)])
        compA_GItoXY2 = self.env['stock.move'].search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', XY2.id),('product_id', '=', self.CompA.id)])
        compB_GItoXY2 = self.env['stock.move'].search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', XY2.id),('product_id', '=', self.CompB.id)])
        #Push rule (Gi -> Stores) applied to over-order (from MOQ, etc.) as per stock_move_push_leftover
        compA_GItoStores = self.env['stock.move'].search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.Stores.id),('product_id', '=', self.CompA.id)])
        compB_GItoStores = self.env['stock.move'].search([('location_id', '=', self.goodsIn.id), ('location_dest_id', '=', self.Stores.id),('product_id', '=', self.CompB.id)])
        compA_StorestoHust = self.env['stock.move'].search([('location_id', '=', self.Stores.id), ('location_dest_id', '=', self.HUST.id),('product_id', '=', self.CompA.id)])
        subA_StorestoHust = self.env['stock.move'].search([('location_id', '=', self.Stores.id), ('location_dest_id', '=', self.HUST.id),('product_id', '=', self.SubA.id)])
                
        self.assertEqual(len(receipt_compA), 1, msg='Not  1 stock move') 
        self.assertEqual(len(receipt_compB), 1, msg='Not  1 stock move') 
        self.assertEqual(len(compA_GItoHUST), 1, msg='Not  1 stock move') 
        self.assertEqual(len(compA_GItoXY2), 1, msg='Not  1 stock move') 
        self.assertEqual(len(compB_GItoXY2), 1, msg='Not  1 stock move') 
        self.assertEqual(len(compA_GItoStores), 1, msg='Not  1 stock move') 
        self.assertEqual(len(compB_GItoStores), 1, msg='Not  1 stock move') 
        self.assertEqual(len(compA_StorestoHust), 1, msg='Not  1 stock move') 
        self.assertEqual(len(subA_StorestoHust), 1, msg='Not  1 stock move') 

        self.assertEqual(receipt_compA.product_uom_qty, 55.0) 
        self.assertEqual(receipt_compB.product_uom_qty, 100.0) 
        self.assertEqual(compA_GItoHUST.product_uom_qty, 48.0) 
        self.assertEqual(compA_GItoXY2.product_uom_qty, 3.0) 
        self.assertEqual(compB_GItoXY2.product_uom_qty, 42.0) 
        self.assertEqual(compA_GItoStores.product_uom_qty, 4.0) 
        self.assertEqual(compB_GItoStores.product_uom_qty, 58.0) 
        self.assertEqual(compA_StorestoHust.product_uom_qty, 2.0) 
        self.assertEqual(subA_StorestoHust.product_uom_qty, 1.0) 


        #Execute receipts
        self.assertEqual(len(receipt_compA.move_line_ids), 1, msg='Not 1 line in incoming stock move') 
        receipt_compA.move_line_ids.qty_done = 55.0
        receipt_compA._action_done()
        self.assertEqual(receipt_compA.state, 'done')

        self.assertEqual(len(receipt_compB.move_line_ids), 1, msg='Not 1 line in incoming stock move') 
        receipt_compB.move_line_ids.qty_done = 100.0
        receipt_compB._action_done()
        self.assertEqual(receipt_compA.state, 'done')

        #Check that CompA was sent directly to the bin that already had some, as per stock_location_savespace
        self.assertEqual(compA_GItoStores.move_line_ids.location_dest_id.id, self.Shelf1.id)
