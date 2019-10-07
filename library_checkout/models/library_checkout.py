from odoo import api,  exceptions, fields, models

class Checkout(model.Model):
    _name='library.checkout'
    _description='Checkout Request'
    member_id = fields.Many2one('library.member', required=True)
    user_id=fields.Many2one('res.users', 'Librarian', default=lambda s: s.env.uid)
    request_date = fields.Dat(default = lambda s: fields.Date.today())
    line_ids = fields.One2many('library.checkout.line', 'checkout_id', string='Borrowed Books',)


class CheckoutLine(models.Model):
    _name='library.checkout.line'
    _description = 'Borrow Request Line'
    checkout_id = fields.Many2one('library.chekcout')
    book_id = fields.Many2one('libary.book')