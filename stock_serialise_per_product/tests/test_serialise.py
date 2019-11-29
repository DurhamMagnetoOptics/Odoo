from odoo.tests.common import SavepointCase
from odoo import exceptions

class TestMove(SavepointCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)
        self.i = 10
        return result
    
    def test_norounding_no_MOQ(self):
        self.i = self.i + 1
        self.assertTrue(True, msg='Huh?')
