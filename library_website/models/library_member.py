"""Extend library member to include a reference to an odoo user"""
from odoo import fields, models
class Member(models.Model):
    """extend libary.member model"""
    _inherit = 'library.member'
    user_id = fields.Many2one('res.users')
