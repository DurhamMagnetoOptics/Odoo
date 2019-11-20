from odoo.tests.common import SavepointCase
from odoo import exceptions

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
        self.TriggerPO = self.rule.create({
            'name': 'Trigger PO',
            'action': 'buy',
            'picking_type_id': self.warehouse.in_type_id.id,
            'location_id': self.goodsIn.id,
            'route_id': self.ComponentResupply.id,
            'sequence': 25,
        })          


        #create Suplier
        self.supplierCompA = self.env['product.supplierinfo'].create({
            'product_tmpl_id': self.CompA.product_tmpl_id.id,
            'name': self.ref('base.res_partner_12'),
            'delay': 1,
            'min_qty': 10.0,
            'increment_qty': 5.0,
            'price': 2.50,
            'round_up': True
        })
            


        #Confirm any existing RFQs for the supplier of interest, so we don't muddy up our test results.
        myPOs = self.env['purchase.order'].search([('partner_id', '=', self.supplierCompA.name.id),('state', '=', 'draft')])
        for PO in myPOs:
            PO.button_confirm()

        return result
    
    def test_norounding(self):
        "Verify normal behaviour (order exaclty the demand) when round_up is off and no MOQ"

        self.supplierCompA.round_up = False
        self.supplierCompA.min_qty = 0.0

        neededQty = 4.0
        expectedOrderQty = neededQty

        #Create procurement
        values = {
            'warehouse_id': self.warehouse,
            'route_ids': self.ComponentResupply,
        }
        PG = self.env['procurement.group']
        strOrigin = 'product_supplierinfo_round_up Test Replenishment'
        
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

        myPOs = self.env['purchase.order'].search([('partner_id', '=', self.supplierCompA.name.id),('state', '=', 'draft')])
        self.assertEqual(len(myPOs), 1, msg='There is not 1 PO generated')
        self.assertEqual(len(myPOs.order_line), 1, msg='There is not 1 line in the PO')
        self.assertEqual(len(myPOs.order_line.product_qty), expectedOrderQty, msg='The PO is not for %s units' % expectedOrderQty)
        self.assertEqual(len(myPOs.order_line.desired_qty), neededQty, msg='The PO does not store an underlying need for %s units' % neededQty)


    def test_norounding(self):
        "Verify normal behaviour (exception for no seller found) when round_up is off and MOQ not met"

        self.supplierCompA.round_up = False

        neededQty = 4.0
        expectedOrderQty = neededQty

        #Create procurement
        values = {
            'warehouse_id': self.warehouse,
            'route_ids': self.ComponentResupply,
        }
        PG = self.env['procurement.group']
        strOrigin = 'product_supplierinfo_round_up Test Replenishment'
        
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
            #Raises error becuase no valid seller/pricebreak found.
            PG.run([proc])