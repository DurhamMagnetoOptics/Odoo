from odoo import models, fields, api
from collections import defaultdict

class account_payment(models.Model):
    _inherit = "account.payment"

    def action_register_payment(self):
        #override default method to always use the view_account_payment_form_multi wizard
        res = super().action_register_payment()
        if res:
            res['res_model'] = 'account.payment.register'
            res['view_id'] = self.env.ref('account.view_account_payment_form_multi').id
            #The following three valaues are only set in the context when we are coming from the aged partner reports, and they result in behaviour Ian doesn't like, so we'll clear them.
            old_context = res['context']
            if 'model' in old_context.keys() or 'default_type' in old_context.keys() or 'default_journal_id' in old_context.keys():
                new_context = dict(old_context).copy()
                new_context.pop('model', False)
                new_context.pop('default_type', False)
                new_context.pop('default_journal_id', False)
                res['context'] = new_context
        return res

class payment_register(models.TransientModel):
    _inherit = "account.payment.register"
    
    live_amount = fields.Monetary(string='Amount', compute="_compute_live_amount", readonly=True)
    currency_id = fields.Many2one('res.currency', compute ="_compute_live_amount", string='Currency', required=True, readonly=True, default=lambda self: self.env.company.currency_id)

    @api.depends('journal_id', 'invoice_ids', 'payment_date')
    def _compute_live_amount(self):
        self.currency_id = self.journal_id.currency_id
        invoices = self.env["account.move"]
        for inv in self.invoice_ids:
            invoices += inv
        self.live_amount = abs(self.env['account.payment']._compute_payment_amount(invoices, self.currency_id, self.journal_id, self.payment_date))
        
