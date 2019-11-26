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


        #Create routes
        self.route = self.env['stock.location.route']
        self.rule = self.env['stock.rule']    
        self.SubassyResupply = self.route.create({
            'name': 'Subassembly Resupply',
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
        self.SubA = self.product.create({
            'name': 'SubA',
            'categ_id': self.ref('product.product_category_5'),
            'standard_price': 100.0,
            'list_price': 50.0,
            'type': 'product',
            'weight': 0.01,
            'uom_id': self.uom_xid,
            'uom_po_id': self.uom_xid,
            'description': 'Sub assembly',
            'default_code': 'DMO_XY2',
            'route_ids': [(6,0,[self.SubassyResupply.id])],
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
       


        self.MTOSubAssy = self.rule.create({
            'name': 'Build Subassy',
            'action': 'manufacture',
            'picking_type_id': self.warehouse.manu_type_id.id,
            'location_id': self.HUST.id,
            'route_id': self.SubassyResupply.id,
            'sequence': 30,
        })       
        self.MTOKitting = self.rule.create({
            'name': 'Subassy On Demand',
            'action': 'pull',
            'picking_type_id': self.warehouse.manu_type_id.id,
            'location_src_id': self.HUST.id,
            'location_id': self.CompA.property_stock_production.id,
            'procure_method': 'make_to_order',
            'route_id': self.SubassyResupply.id,
            'sequence': 30,
        })                    
          


        #Create BOMs
        self.MW3_BOM = self.env['mrp.bom'].create({
            'product_tmpl_id': self.MW3.product_tmpl_id.id,
            'product_uom_id': self.ref('uom.product_uom_unit')
        })
        self.subA_BOM_line = self.env['mrp.bom.line'].create({
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
        self.subA_compA_BOM_line = self.env['mrp.bom.line'].create({
            'product_id': self.CompA.id,
            'product_qty': 1.0,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'sequence': 5,
            'bom_id': self.SubA_BOM.id
        })   

        return result

    def test_null(self):
        "Make sure multilevel_kitting off creates the need in-situ, even with multilevel_kitting name set on BOM"

        self.warehouse.manu_type_id.multilevel_kitting = False

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

        #Check that a new MO is created for XY2, and that it has HUST as destination and HUST or XY2 as source, depending on the test case.
        #Tests: with boolean Off.  With boolean on but name blank.  With boolean on and name filled in and location doesn't exist.  With boolean on and name filled in and location does exist.
        myMOs = self.env['mrp.production'].search([('product_id.id', '=', self.SubA.id)])
        self.assertEqual(len(myMOs), 1, msg='Not 1 MO generated for SubA')
        self.assertEqual(myMOs.location_src_id.id, self.HUST.id, msg='Source location not HUST')
        self.assertEqual(myMOs.location_dest_id.id, self.HUST.id, msg='Destination location not HUST')

    def test_enabled_noname(self):
        "Make sure multilevel_kitting kits in place when enabled with no name on the BOM."

        self.warehouse.manu_type_id.multilevel_kitting = True
        self.SubA_BOM.multilevel_kitting_name = False

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

        myMOs = self.env['mrp.production'].search([('product_id.id', '=', self.SubA.id)])
        self.assertEqual(len(myMOs), 1, msg='Not 1 MO generated for SubA')
        self.assertEqual(myMOs.location_src_id.id, self.HUST.id, msg='Source location not HUST')
        self.assertEqual(myMOs.location_dest_id.id, self.HUST.id, msg='Destination location not HUST')        

    def test_enabled_namenotexist(self):
        "Make sure multilevel_kitting off creates the need in the sub location when enabled and the sublocation doesn't yet exist"

        self.warehouse.manu_type_id.multilevel_kitting = True

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

        myMOs = self.env['mrp.production'].search([('product_id.id', '=', self.SubA.id)])
        self.assertEqual(len(myMOs), 1, msg='Not 1 MO generated for SubA')
        #TODO: when working soure location will be named 'XY2' and its parent will be HUST
        self.assertEqual(myMOs.location_src_id.name, self.SubA_BOM.multilevel_kitting_name, msg='Source location not %s' % self.SubA_BOM.multilevel_kitting_name)
        self.assertEqual(myMOs.location_src_id.location_id.id, self.HUST.id, msg='Source location not a child if HUST')
        self.assertEqual(myMOs.location_dest_id.id, self.HUST.id, msg='Destination location not HUST')        

    def test_enabled_nameexist(self):
        "Make sure multilevel_kitting off creates the need in the sublocation when enabled the the sublocation already exists"

        self.warehouse.manu_type_id.multilevel_kitting = True
        XY2 = self.Location.create({
            'name': self.SubA_BOM.multilevel_kitting_name,
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

        myMOs = self.env['mrp.production'].search([('product_id.id', '=', self.SubA.id)])
        self.assertEqual(len(myMOs), 1, msg='Not 1 MO generated for SubA')

        self.assertEqual(myMOs.location_src_id.id, XY2.id, msg='Source location not HUST')
        self.assertEqual(myMOs.location_dest_id.id, self.HUST.id, msg='Destination location not HUST')              
