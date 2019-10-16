""" Temporary test of web controllers"""
from odoo import http
from odoo.http import request

class Hello(http.Controller):
    @http.route('/helloworld', auth='public', website=True)
    def helloworld(self, **kwargs):
        return request.render('library_website.helloworld')
