from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"
    
    require_ref = fields.Boolean(related='company_id.require_ref')

    def button_payments(self):
        return {
            'name': 'Payments',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'views': [(self.env.ref('account.view_account_payment_tree').id, 'tree'), (self.env.ref('account.view_account_payment_form').id, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('invoice_ids', '=', self.id)], 
            'context': {'create': False},
        }    