# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'DMO Accounting',
    'summary': 'Various tweaks to Odoo accounting to better match DMO work flow',
    'version': '13.0.1.0.0',
    'development_status': 'caveat emptor',
    'category': 'Accounting',
    'website': 'http://www.dmoltd.co.uk',
    'author': 'Durham Magneto Optics Ltd',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'account_accountant',
    ],
    'data': [
        'views/account_move_views.xml',
        'views/view_company_form.xml',
    ],
    'demo': [
        
    ]
}
