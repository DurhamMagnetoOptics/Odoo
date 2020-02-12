from odoo.tests.common import SavepointCase
from odoo import exceptions

class TestMove(SavepointCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)

        self.warehouse = self.env.ref('stock.warehouse0')
        self.uom_xid = self.ref('uom.product_uom_unit')

        #Create Locations
        self.Location = self.env['stock.location']
        self.Builds = self.Location.create({
            'name': 'Builds',
            'location_id': self.warehouse.view_location_id.id
        })                                
        self.HUST = self.Location.create({
            'name': 'HUST',
            'location_id': self.Builds.id
        })               
            

        #Clear default locations on Manufacturing Operation
        self.warehouse.manu_type_id.default_location_dest_id = False
        self.warehouse.manu_type_id.default_location_src_id = False         


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
        })                  
        self.CompB = self.product.create({
            'name': 'CompB',
            'categ_id': self.ref('product.product_category_5'),
            'standard_price': 10,
            'list_price': 10,
            'type': 'product',
            'weight': 0.01,
            'uom_id': self.uom_xid,
            'uom_po_id': self.uom_xid,
            'description': 'Sheet component',
            'default_code': 'MK-12345',
        })               
          


        #Create BOMs
        self.MW3_BOM = self.env['mrp.bom'].create({
            'product_tmpl_id': self.MW3.product_tmpl_id.id,
            'product_uom_id': self.ref('uom.product_uom_unit')
        })
        self.compA_BOM_line = self.env['mrp.bom.line'].create({
            'product_id': self.CompA.id,
            'product_qty': 2.0,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'sequence': 5,
            'bom_id': self.MW3_BOM.id
        })          
        self.compB_BOM_line = self.env['mrp.bom.line'].create({
            'product_id': self.CompB.id,
            'product_qty': 1.0,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'sequence': 5,
            'bom_id': self.MW3_BOM.id
        })   

        return result

    def test_null1(self):
        "Make sure multilevel_kitting off creates the need in-situ as normal"

        self.warehouse.manu_type_id.multilevel_kitting = False
        self.MW3_BOM.multilevel_kitting = True
        self.compA_BOM_line.multilevel_kitting_name = "TestBin"

        #create MO
        strOrigin = 'mrp_multilevel_kitting Test Replenishment'
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
        move1 = myMoves.search([('location_id', '=', self.HUST.id), ('product_id', '=', self.CompA.id)])
        move2 = myMoves.search([('location_id', '=', self.HUST.id), ('product_id', '=', self.CompB.id)])

        self.assertEqual(len(move1), 1, msg='Expected move of CompA not found')
        self.assertEqual(len(move2), 1, msg='Expected move of CompB not found')

    def test_null2(self):
        "Make sure multilevel_kitting off creates the need in-situ as normal"

        self.warehouse.manu_type_id.multilevel_kitting = True
        self.MW3_BOM.multilevel_kitting = False
        self.compA_BOM_line.multilevel_kitting_name = "TestBin"

        #create MO
        strOrigin = 'mrp_multilevel_kitting Test Replenishment'
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
        move1 = myMoves.search([('location_id', '=', self.HUST.id), ('product_id', '=', self.CompA.id)])
        move2 = myMoves.search([('location_id', '=', self.HUST.id), ('product_id', '=', self.CompB.id)])

        self.assertEqual(len(move1), 1, msg='Expected move of CompA not found')
        self.assertEqual(len(move2), 1, msg='Expected move of CompB not found')

    def test_null3(self):
        "Make sure multilevel_kitting on but no bin name creates the need in-situ as normal"

        self.warehouse.manu_type_id.multilevel_kitting = True
        self.MW3_BOM.multilevel_kitting = True
        self.compA_BOM_line.multilevel_kitting_name = ''

        #create MO
        strOrigin = 'mrp_multilevel_kitting Test Replenishment'
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
        move1 = myMoves.search([('location_id', '=', self.HUST.id), ('product_id', '=', self.CompA.id)])
        move2 = myMoves.search([('location_id', '=', self.HUST.id), ('product_id', '=', self.CompB.id)])

        self.assertEqual(len(move1), 1, msg='Expected move of CompA not found')
        self.assertEqual(len(move2), 1, msg='Expected move of CompB not found')             

    def test_samebinexist(self):
        "Make sure multilevel_kitting off creates the need in-situ as normal"

        self.warehouse.manu_type_id.multilevel_kitting = True
        self.MW3_BOM.multilevel_kitting = True
        self.compA_BOM_line.multilevel_kitting_name = "TestBin"
        self.compB_BOM_line.multilevel_kitting_name = "TestBin"
        testBin = self.Location.create({
            'name': 'TestBin',
            'location_id': self.HUST.id
        })  

        #create MO
        strOrigin = 'mrp_multilevel_kitting Test Replenishment'
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
        move1 = myMoves.search([('location_id', '=', testBin.id), ('product_id', '=', self.CompA.id)])
        move2 = myMoves.search([('location_id', '=', testBin.id), ('product_id', '=', self.CompB.id)])

        self.assertEqual(len(move1), 1, msg='Expected move of CompA not found')
        self.assertEqual(len(move2), 1, msg='Expected move of CompB not found')           

    def test_samebincreated(self):
        "Make sure multilevel_kitting off creates the need in-situ as normal"

        self.warehouse.manu_type_id.multilevel_kitting = True
        self.MW3_BOM.multilevel_kitting = True
        self.compA_BOM_line.multilevel_kitting_name = "TestBin"
        self.compB_BOM_line.multilevel_kitting_name = "TestBin"


        #create MO
        strOrigin = 'mrp_multilevel_kitting Test Replenishment'
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
        move1 = myMoves.search([('product_id', '=', self.CompA.id)])
        move2 = myMoves.search([('product_id', '=', self.CompB.id)])

        self.assertEqual(len(move1), 1, msg='Expected move of CompA not found')
        self.assertEqual(len(move2), 1, msg='Expected move of CompB not found')  

        self.assertEqual(move1.location_id.location_id.id, self.HUST.id, msg='CompA not drawn from child of source')          
        self.assertEqual(move1.location_id.id, move2.location_id.id, msg='Different bins for compA and compB')     

        self.assertEqual(move1.location_id.name, "TestBin", msg='CompA not drawn from child of source')

    def test_diffbins(self):
        "Make sure multilevel_kitting off creates the need in-situ as normal"

        self.warehouse.manu_type_id.multilevel_kitting = True
        self.MW3_BOM.multilevel_kitting = True
        self.compA_BOM_line.multilevel_kitting_name = "TestBin1"
        self.compB_BOM_line.multilevel_kitting_name = "TestBin2"

        testBin1 = self.Location.create({
            'name': 'TestBin1',
            'location_id': self.HUST.id
        })  


        #create MO
        strOrigin = 'mrp_multilevel_kitting Test Replenishment'
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
        move1 = myMoves.search([('product_id', '=', self.CompA.id)])
        move2 = myMoves.search([('product_id', '=', self.CompB.id)])

        self.assertEqual(len(move1), 1, msg='Expected move of CompA not found')
        self.assertEqual(len(move2), 1, msg='Expected move of CompB not found')  

        self.assertEqual(move1.location_id.id, testBin1.id, msg='CompA not drawng from existing location') 
        
        self.assertEqual(move2.location_id.name, "TestBin2", msg='CompB location incorrect name')        
        self.assertEqual(move2.location_id.location_id.id, self.HUST.id, msg='CompB not drawn from child of source')              

    def test_diffbinsoneblank(self):
        "Make sure multilevel_kitting off creates the need in-situ as normal"

        self.warehouse.manu_type_id.multilevel_kitting = True
        self.MW3_BOM.multilevel_kitting = True
        self.compA_BOM_line.multilevel_kitting_name = "TestBin1"
        self.compB_BOM_line.multilevel_kitting_name = ''

        testBin1 = self.Location.create({
            'name': 'TestBin1',
            'location_id': self.HUST.id
        })  


        #create MO
        strOrigin = 'mrp_multilevel_kitting Test Replenishment'
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
        move1 = myMoves.search([('product_id', '=', self.CompA.id)])
        move2 = myMoves.search([('product_id', '=', self.CompB.id)])

        self.assertEqual(len(move1), 1, msg='Expected move of CompA not found')
        self.assertEqual(len(move2), 1, msg='Expected move of CompB not found')  

        self.assertEqual(move1.location_id.id, testBin1.id, msg='CompA not drawng from existing location') 
        self.assertEqual(move2.location_id.id, self.HUST.id, msg='CompB not from source')  

    def test_diffbinsotherblank(self):
        "Make sure multilevel_kitting off creates the need in-situ as normal"

        self.warehouse.manu_type_id.multilevel_kitting = True
        self.MW3_BOM.multilevel_kitting = True
        self.compA_BOM_line.multilevel_kitting_name = ''
        self.compB_BOM_line.multilevel_kitting_name = "TestBin2"

        testBin1 = self.Location.create({
            'name': 'TestBin1',
            'location_id': self.HUST.id
        })  


        #create MO
        strOrigin = 'mrp_multilevel_kitting Test Replenishment'
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
        move1 = myMoves.search([('product_id', '=', self.CompA.id)])
        move2 = myMoves.search([('product_id', '=', self.CompB.id)])

        self.assertEqual(len(move1), 1, msg='Expected move of CompA not found')
        self.assertEqual(len(move2), 1, msg='Expected move of CompB not found')  

        self.assertEqual(move1.location_id.id, self.HUST.id, msg='CompA not drawng from source') 
        
        self.assertEqual(move2.location_id.name, "TestBin2", msg='CompB location incorrect name')                      
        self.assertEqual(move2.location_id.location_id.id, self.HUST.id, msg='CompB not drawn from child of source')              