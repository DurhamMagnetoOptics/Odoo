# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.tools.misc import format_date


class report_account_aged_partner(models.AbstractModel):
    _inherit = "account.aged.partner"

    def _get_columns_name(self, options):
        columns = super()._get_columns_name(options)
        if self.env.company.dmo_aged:
            for i, col in enumerate(columns):
                if col.get('name') == "Journal":
                    columns[i] = {'name': "Journal2", 'class': '', 'style': 'text-align:center; white-space:nowrap;'}
                    #If we change this column to a date we'll want to base it on the following template, instead:
                    #{'name': _("Due Date"), 'class': 'date', 'style': 'white-space:nowrap;'},
                elif col.get('name') == "Account":
                    columns[i] = {'name': "Account", 'class': '', 'style': 'text-align:center; white-space:nowrap;'}
        return columns
        


    @api.model
    def _get_lines(self, options, line_id=None):
        lines = super()._get_lines(options, line_id)
        if self.env.company.dmo_aged:
            for vals in lines:
                if vals.get('level') == 4:
                    vals['columns'][2]['name'] = vals['columns'][2]['name'] + '_DMO'     
                    #From parent, this is:
                    #'columns': [{'name': v} for v in [format_date(self.env, aml.date_maturity or aml.date), aml.journal_id.code, aml.account_id.display_name, format_date(self.env, aml.expected_pay_date)]] + [{'name': self.format_value(sign * v, blank_if_zero=True), 'no_format': sign * v} for v in [line['period'] == 6-i and line['amount'] or 0 for i in range(7)]],
                    #One of the entries in vals is the aml)id, which will let us load the account.move.line, as below, to extract the other information Ian wants.
                    #self.env['account.move.line'].browse(aml_ids):
        return lines
