# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'DMO Accounting',
    'summary': 'Various tweaks to Odoo accounting to better match DMO work flow',
    'version': '13.1.0.0.0',
    'development_status': 'caveat emptor',
    'category': 'Accounting',
    'website': 'http://www.dmoltd.co.uk',
    'author': 'Durham Magneto Optics Ltd',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'account_accountant',
        'account_reports',
    ],
    'data': [
        'views/account_move_views.xml',
        'views/view_company_form.xml',
        'views/account_payment_view.xml',
        'views/report_payment_receipt_templates.xml',
        'views/account_financial_report_data.xml',
    ],
    'demo': [
        
    ]
}
