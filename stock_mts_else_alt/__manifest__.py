# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MTS else Alternate Rule',
    'summary': 'Modify MTS else MTO to actually execute an alternate rule instead of automatically running MTS in the same source location',
    'version': '13.0.1.0.0',
    'development_status': 'Mature',
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
        'view/pull_rule.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ]
}
