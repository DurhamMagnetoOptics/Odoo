{
    'name': 'Library Book Borrowing',
    'description': 'Members can borrow books from the library.',
    'author': 'Daniel Reis',
    'depends': ['library_member'],
    'application': False,
    'data': [
        'security/ir.model.access.csv',
        'views/library_menu.xml',
        'views/checkout_view.xml',
    ]    
}