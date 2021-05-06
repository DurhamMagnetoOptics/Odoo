# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Replenish In-Place',
    'summary': 'Allows the user to request stock replenishment in a specific location',
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
        'views/product_replenish_views.xml',
    ],
    'demo': [
        
    ]
}
