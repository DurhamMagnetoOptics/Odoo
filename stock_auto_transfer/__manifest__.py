# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Auto Transfer',
    'summary': 'Expand the stock scheduler to automate the creation of certain stock moves',
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
        'views/stock_picking_views.xml',
        'views/stock_location_views.xml',
    ],
    'demo': [
        
    ]
}
