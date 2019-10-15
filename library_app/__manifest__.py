{
    'name': 'Library Managment',
    'description': 'Manage library book catalogue and lending.',
    'author': 'Daniel Reis',
    'depends': ['base'],
    'application': True,
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/library_menu.xml',
        'views/book_view.xml',
        'views/book_list_template.xml',
        ],
    'demo': [
        'data/res.partner.csv',
        'data/library.book.csv',
        'data/book_demo.xml',
        'reports/library_book_report.xml',
        ]        
}