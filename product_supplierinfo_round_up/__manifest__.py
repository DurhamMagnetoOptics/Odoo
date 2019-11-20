# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Round PO up to supplier MOQ',
    'summary': 'When no supplierinfo is found for the desired quantity, increase the ordered quanity to meet the supplier minimum',
    'version': '13.0.1.0.0',
    'development_status': 'caveat emptor',
    'category': 'Warehouse',
    'website': 'http://www.dmoltd.co.uk',
    'author': 'Durham Magneto Optics Ltd',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'stock',
        'purchase',
    ],
    'data': [
        'views/product_views.xml',
    ],
    'demo': [
        
    ]
}
