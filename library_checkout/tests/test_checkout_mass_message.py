from odoo.tests.common import TransactionCase

class TestWizard(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestWizard, self).setUp(*args, **kwargs)
        #Add test setup code here....
    
    def test_button_send(self):
        """Send button shouhld create messages on CHeckouts"""
        #Add test code