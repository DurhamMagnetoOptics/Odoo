# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'DMO JIT2',
    'summary': 'Top level app to collect stock an mrp mods, and integrated demo data',
    'version': '13.1.0.0.0',
    'development_status': 'Test purposes only',
    'category': 'Manufacture',
    'website': 'http://www.dmoltd.co.uk',
    'author': 'Durham Magneto Optics Ltd',
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'depends': [
        'dmo_meta_data',
        'mrp_bom_lot',
        'mrp_multilevel_kitting',
        'stock_location_savespace',
        'stock_replenish_inplace',
        'stock_serialise_per_product',
    ],
    'data': [
        
    ],
    'demo': [
        'demo/data.xml',
    ]
}
