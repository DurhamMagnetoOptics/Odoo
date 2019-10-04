class TestBook(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)
        user_admin = self.env.ref('base.user_admin')
        self.env = self.env(user=user_admin)
        self.Book = self.env['library.book']
        self.book_ode = self.Book.create({
            'name': 'Lord of the Flies',
            'isbn': '0-571-05686-5'
        })
        return result
    
    def test_check_isbn(self):
        "Check valid ISBN"
        self.assertTrue(self.book_ode._check_isbn)