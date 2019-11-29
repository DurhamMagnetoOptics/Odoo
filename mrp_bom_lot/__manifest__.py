# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MRP BOM Lot',
    'summary': 'Create a link between BOM and lot/serial number',
    'version': '13.0.1.0.0',
    'development_status': 'caveat emptor',
    'category': 'Warehouse',
    'website': 'http://www.dmoltd.co.uk',
    'author': 'Durham Magneto Optics Ltd',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'mrp',
    ],
    'data': [
        'views/product_views.xml',
        'views/stock_production_lot_views.xml',
    ],
    'demo': [
        
    ]
}
