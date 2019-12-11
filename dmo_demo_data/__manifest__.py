# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


##TODO: add those UK accounting modules (and anything else to make it look like our prod DB) for the benefit of odoo.sh dev servers??
{
    'name': 'DMO Demo Data',
    'summary': 'A place to throw demo data and tests that cross module boundaries',
    'version': '13.0.1.0.0',
    'development_status': 'Test purposes only',
    'category': 'Manufacture',
    'website': 'http://www.dmoltd.co.uk',
    'author': 'Durham Magneto Optics Ltd',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'stock_mts_else_alt',
        'stock_move_push_leftover',
        'mrp_apply_parent_pull',
        'product_supplierinfo_round_up',
        'stock_location_savespace',
        'mrp_multilevel_kitting',
        'mrp_bom_lot',
        'stock_serialise_per_product',
        'stock',
        'purchase',
        'purchase_stock',
    ],
    'data': [
        
    ],
    'demo': [
        'demo/data.xml',
    ]
}
