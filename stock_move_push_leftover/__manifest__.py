# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Move Push Leftover',
    'summary': 'When a stock move is committed, any quantity not accounted for by child moves is split off and submitted to push rules instead',
    'version': '13.0.2.0.0',
    'development_status': 'caveat emptor',
    'category': 'Warehouse',
    'website': 'http://www.dmoltd.co.uk',
    'author': 'Durham Magneto Optics Ltd',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'stock','purchase','purchase_stock',
    ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'demo': [
        
    ]
}
