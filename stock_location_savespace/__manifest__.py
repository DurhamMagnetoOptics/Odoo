# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Location Save Space',
    'summary': 'If a product is already in stock in a child location, and no other putaway rule applies, use the existing location as the putaway target',
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
    ],
    'data': [
        'views/stock_location_views.xml',
    ],
    'demo': [
        
    ]
}
