from odoo.tests.common import TransactionCase

class TestBook(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)
        user_admin = self.env.ref('base.user_admin')
        self.env = self.env(user=user_admin)
        self.Book = self.env['library.book']
        #How do I create two different books so I can also test the 13-digit ISBN pass-through as well as the new 10-digit check?
        self.book_ode = self.Book.create({
            'name': 'Lord of the Flies',
            'isbn': '0-571-05686-5'
        })
        return result

    #This only tests the len(10) branch
    def test_check_isbn(self):
        "Check valid ISBN"
        self.assertTrue(self.book_ode._check_isbn)        