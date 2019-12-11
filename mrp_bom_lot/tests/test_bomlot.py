from odoo.tests.common import SavepointCase
from odoo import exceptions


class TestBomLot(SavepointCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)

        #Create defaults
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.uom_xid = self.ref('uom.product_uom_unit')
        self.company = self.env.ref('stock.warehouse0').company_id
        self.prodlot = self.env['stock.production.lot']

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
            'company_id': self.company.id,
        })
        self.CompA = self.product.create({
            'name': 'CompA',
            'categ_id': self.ref('product.product_category_5'),
            'standard_price': 2.5,
            'list_price': 2.5,
            'type': 'consu',
            'weight': 0.01,
            'uom_id': self.uom_xid,
            'uom_po_id': self.uom_xid,
            'description': 'Machined Component',
            'default_code': 'PL-12345',
            'company_id': self.company.id,
        })           

        #Create BOM
        self.MW3_BOM = self.env['mrp.bom'].create({
            'product_tmpl_id': self.MW3.product_tmpl_id.id,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'code': 'Old',
            'sequence': 10
        })
        self.compA_BOM_line = self.env['mrp.bom.line'].create({
            'product_id': self.CompA.id,
            'product_qty': 5.0,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'sequence': 5,
            'bom_id': self.MW3_BOM.id
        })   

        #Create Newer BOM
        self.new_MW3_BOM = self.env['mrp.bom'].create({
            'product_tmpl_id': self.MW3.product_tmpl_id.id,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'code': 'New',
            'sequence': 5
        })
        self.new_compA_BOM_line = self.env['mrp.bom.line'].create({
            'product_id': self.CompA.id,
            'product_qty': 5.0,
            'product_uom_id': self.ref('uom.product_uom_unit'),
            'sequence': 5,
            'bom_id': self.new_MW3_BOM.id
        })           

        return result
    
    def test_nolink(self):
        strName = 'AB100C'
        lot1 = self.prodlot.create({
            'name': strName,
            'product_id': self.MW3.id,
            'company_id': self.company.id,
            'bom_id': self.MW3_BOM.id
        })

        self.MW3.link_BOM_to_lot = False
        self.CompA.link_BOM_to_lot = False

        lot1.product_id = self.CompA.id
        self.assertEqual(lot1.bom_id.id, self.MW3_BOM.id)     

    def test_changeproduct(self):
        strName = 'AB100C'
        lot1 = self.prodlot.create({
            'name': strName,
            'product_id': self.MW3.id,
            'company_id': self.company.id,
            'bom_id': self.MW3_BOM.id
        })


        self.MW3.link_BOM_to_lot = True
        self.CompA.link_BOM_to_lot = True

        lot1.product_id = self.CompA.id
        self.assertFalse(lot1.bom_id)    

        lot1.product_id = self.MW3.id
        self.assertEqual(lot1.bom_id.id, self.new_MW3_BOM.id)        

    def test_action(self):
        self.MW3.link_BOM_to_lot = True

        #create MO
        strOrigin = 'mrp_bom_lot Test Production'
        self.MW3_MO = self.env['mrp.production'].create({
            'name': strOrigin,
            'origin': strOrigin,
            'product_tmpl_id': self.MW3.product_tmpl_id.id,
            'product_id': self.MW3.id,
            'product_qty': 1.0,
            'bom_id': self.MW3_BOM.id,
            'product_uom_id': self.ref('uom.product_uom_unit')
        })      
        self.MW3_MO._onchange_move_raw()
        self.MW3_MO.action_confirm()    

        
        wiz1 = self.env['mrp.product.produce'].with_context(active_id=self.MW3_MO.id, active_ids=[self.MW3_MO.id], active_model='mrp.production').create({})
        wiz1.action_generate_serial()    
        self.assertEqual(wiz1.finished_lot_id.bom_id.id, self.MW3_BOM.id)

    def test_null_action(self):
        self.MW3.link_BOM_to_lot = False

        #create MO
        strOrigin = 'mrp_bom_lot Test Production'
        self.MW3_MO = self.env['mrp.production'].create({
            'name': strOrigin,
            'origin': strOrigin,
            'product_tmpl_id': self.MW3.product_tmpl_id.id,
            'product_id': self.MW3.id,
            'product_qty': 1.0,
            'bom_id': self.MW3_BOM.id,
            'product_uom_id': self.ref('uom.product_uom_unit')
        })      
        self.MW3_MO._onchange_move_raw()
        self.MW3_MO.action_confirm()    

        
        wiz1 = self.env['mrp.product.produce'].with_context(active_id=self.MW3_MO.id, active_ids=[self.MW3_MO.id], active_model='mrp.production').create({})
        wiz1.action_generate_serial()    
        self.assertFalse(wiz1.finished_lot_id.bom_id)        