# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MRP Multi-level Kitting',
    'summary': 'If specified on the bom line, the source location for each moveis set to a sublocation of the MOs soure',
    'version': '13.1.0.0.0',
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
        'views/mrp_bom_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_move_views.xml',
    ],
    'demo': [
        
    ]
}
