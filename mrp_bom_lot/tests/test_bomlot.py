from odoo.tests.common import SavepointCase
from odoo import exceptions


class TestBomLot(SavepointCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)

        #Create product
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.product = self.env['product.product']
        self.company = self.env.ref('stock.warehouse0').company_id
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
            'company_id': self.company.id,
        })            

        #get lot
        self.prodlot = self.env['stock.production.lot']

        return result
    
    def test_notracking(self):
        self.CompA.tracking = 'none'
        strName = 'AB100C'
        lot1 = self.prodlot.create({
            'name': strName,
            'product_id': self.CompA.id,
            'company_id': self.company.id
        })

        self.assertEqual(lot1.name, strName)   