from odoo.tests.common import SavepointCase
from odoo import exceptions

class TestMove(SavepointCase):
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

    def test_defaultseq(self):
        self.CompA.tracking = 'lot'
        strName = 'AB100C'
        lot1 = self.prodlot.create({
            'name': strName,
            'product_id': self.CompA.id,
            'company_id': self.company.id
        })

        self.assertEqual(lot1.name, strName)    

    def test_defaultseq_noname(self):
        self.CompA.tracking = 'lot'
        strName = ''
        lot1 = self.prodlot.create({
            'name': strName,
            'product_id': self.CompA.id,
            'company_id': self.company.id
        })

        self.assertTrue(lot1.name.isnumeric())          

    def test_customtseq(self):
        #create sequence
        seq = self.env['ir.sequence'].create({
            'prefix': 'AA',
            'suffix': 'BB',
            'padding': 4,
            'number_increment': 5,
            'company_id': self.company.id,
            'implementation': 'standard',
            'name': 'TestSeq1',
        })

        self.CompA.tracking = 'lot'
        self.CompA.sequence_id = seq.id
        strName = 'AB100C'
        lot1 = self.prodlot.create({
            'name': strName,
            'product_id': self.CompA.id,
            'company_id': self.company.id
        })

        self.assertEqual(lot1.name, strName)  

    def test_customtseq_noname(self):
        #create sequence
        seq = self.env['ir.sequence'].create({
            'prefix': 'AA',
            'suffix': 'BB',
            'padding': 4,
            'number_increment': 5,
            'company_id': self.company.id,
            'implementation': 'standard',
            'name': 'TestSeq1',
        })

        self.CompA.tracking = 'lot'
        self.CompA.sequence_id = seq.id
        strName = ''
        lot1 = self.prodlot.create({
            'name': strName,
            'product_id': self.CompA.id,
            'company_id': self.company.id
        })

        self.assertEqual(lot1.name, 'AA0001BB')       

    def test_customtseq_changeprod(self):
        #create sequence
        seq = self.env['ir.sequence'].create({
            'prefix': 'AA',
            'suffix': 'BB',
            'padding': 4,
            'number_increment': 5,
            'company_id': self.company.id,
            'implementation': 'standard',
            'name': 'TestSeq1',
        })

        self.CompA.tracking = 'lot'
        self.CompA.sequence_id = seq.id
        strName = ''
        lot1 = self.prodlot.create({
            'name': strName,
            'product_id': self.CompA.id,
            'company_id': self.company.id
        })

        self.assertEqual(lot1.name, 'AA0001BB')       

        lot1.product_id = self.CompA.id

        self.assertEqual(lot1.name, 'AA0001BB')       

    def test_customtseq_blankname_changeprod(self):
        #create sequence
        seq = self.env['ir.sequence'].create({
            'prefix': 'AA',
            'suffix': 'BB',
            'padding': 4,
            'number_increment': 5,
            'company_id': self.company.id,
            'implementation': 'standard',
            'name': 'TestSeq1',
        })

        self.CompA.tracking = 'lot'
        self.CompA.sequence_id = seq.id
        strName = ''
        lot1 = self.prodlot.create({
            'name': strName,
            'product_id': self.CompA.id,
            'company_id': self.company.id
        })

        self.assertEqual(lot1.name, 'AA0001BB')   

        lot1.name = ''
        lot1.product_id = self.CompA.id

        self.assertEqual(lot1.name, 'AA0006BB')                          
