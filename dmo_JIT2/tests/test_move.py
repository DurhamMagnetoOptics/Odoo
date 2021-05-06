from odoo.tests.common import SavepointCase

class TestMove(SavepointCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)

        return result
    
    def test_complete_flow(self):
        "Test MO -> PO flow, including partial stock, parent pull rule, leftover putaway, and MOQ rounding"
        
        pass