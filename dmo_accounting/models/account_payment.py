from odoo import models, fields, api
from collections import defaultdict

class account_payment(models.Model):
    _inherit = "account.payment"

    def action_register_payment(self):
        res = super().action_register_payment()
        if res:
            #If we have come to the Bill/Invoice view through the aged partner report, there are some incorrect values in the context
            #This isn't actually specific to our "DMO Ageed XXX" reports (aka it happens from Odoo's aged parter reports, too), but
            #  in the interest of being as light-touch as possible, we will only remove them from the context in the case of our custom forms.
            old_context = res['context']
            if old_context and (old_context.get('model', False) == 'account.aged.payabledmo' or old_context.get('model', False) == 'account.aged.receivabledmo'):
                new_context = dict(old_context).copy()
                new_context.pop('model', False)
                new_context.pop('default_type', False)
                new_context.pop('default_journal_id', False)
                res['context'] = new_context
        return res
        
