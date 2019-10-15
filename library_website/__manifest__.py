{
    'name': 'Library Website',
    'description': 'Create and check book checkout requests.',
    'author': 'Daniel Reis',
    'depends': ['library_checkout',],
    'application': False,
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/library_member.xml',
    ]    
}