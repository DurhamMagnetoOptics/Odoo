from odoo import models, fields, api
from collections import defaultdict

class payment_register(models.TransientModel):
    _inherit = "account.payment.register"
    
    live_amount = fields.Monetary(string='Amount', compute="_compute_live_amount", readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True, default=lambda self: self.env.company.currency_id)

    @api.depends('journal_id', 'invoice_ids', 'payment_date')
    def _compute_live_amount(self):
        grouped = defaultdict(lambda: self.env["account.move"])
        for inv in self.invoice_ids:
            grouped['all'] += inv
        invoices = grouped['all']
        self.live_amount = abs(self.env['account.payment']._compute_payment_amount(invoices, invoices[0].currency_id, self.journal_id, self.payment_date))
