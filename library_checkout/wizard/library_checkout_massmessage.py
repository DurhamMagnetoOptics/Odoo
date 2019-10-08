from odoo import api, exceptions, fields, models
import logging
from odoo import exceptions
_logger = logging.getLogger(__name__)

class CheckoutMassMessage(models.TransientModel):
    _name = 'library.checkout.massmessage'
    _description = 'Send Message to Borrowers'
    checkout_ids = fields.Many2many('library.checkout', string='Checkouts')
    message_subject = fields.Char()
    message_body = fields.Html()

    @api.model
    def default_get(self, field_names):
        defaults = super().default_get(field_names)
        checkout_ids = self.env.context.get('active_ids')
        defaults['checkout_ids'] = checkout_ids
        return defaults

    @api.multi
    def button_send(self):
        self.ensure_one()
        if not self.checkout_ids:
            raise exceptions.UserError('Select at least one Checkout to send messages to.')
        _logger.info('Posted %s messages as body', self.message_body)
        if not self.message_body:  #See above output to understand why this is a bad exception test.  The html widget fills it with <p><br></p> by default so even if the user types noting, message_body isn't emtpy.
            raise exceptions.UserError('Write a message body to send.')
        for checkout in self.checkout_ids:
            checkout.message_post(
                body=self.message_body,
                subject=self.message_subject,
                subtype='mail.mt_comment',
            )
            _logger.debug('Posted %d messages to followers: %s', checkout.id, checkout.message_follower_ids)
        _logger.info('Posted %d messages to Checkouts: %s', len(self.checkout_ids), str(self.checkout_ids))
        return True
