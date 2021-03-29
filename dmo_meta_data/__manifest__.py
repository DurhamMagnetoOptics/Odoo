# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'DMO Meta Data',
    'summary': 'Adds various meta data fields of use to DMO',
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
        'purchase',
    ],
    'data': [
        'views/product_views.xml',
        'views/res_partner_views.xml',
        'views/stock_location_views.xml',
    ],
    'demo': [
        
    ]
}
