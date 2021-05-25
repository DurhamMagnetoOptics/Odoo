# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.tools.misc import format_date


class report_account_aged_receivableDMO(models.AbstractModel):
    _name = "account.aged.receivabledmo"
    _description = "DMO Aged Receivable"
    _inherit = "account.aged.receivable"

    def _get_report_name(self):
        return _("DMO Aged Receivable")


    def _get_columns_name(self, options):
        columns = super()._get_columns_name(options)
        for i, col in enumerate(columns):
            if col.get('name') == "Journal":
                columns[i] = {'name': "Invoice Date", 'class': 'date', 'style': 'white-space:nowrap;'}
            elif col.get('name') == "Account":
                columns[i] = {'name': "Ref", 'class': '', 'style': 'text-align:center; white-space:nowrap;'}
        return columns
        


    @api.model
    def _get_lines(self, options, line_id=None):
        lines = super()._get_lines(options, line_id)
        for vals in lines:
            if vals.get('level') == 4:
                aml_id = self.env['account.move.line'].browse(vals['id'])

                vals['columns'][1]['name'] = format_date(self.env, aml_id.move_id.invoice_date) #invoice date
                vals['columns'][2]['name'] = aml_id.move_id.ref #vendor reference  
                
                #From parent, this is:
                #'columns': [{'name': v} for v in [format_date(self.env, aml.date_maturity or aml.date), aml.journal_id.code, aml.account_id.display_name, format_date(self.env, aml.expected_pay_date)]] + [{'name': self.format_value(sign * v, blank_if_zero=True), 'no_format': sign * v} for v in [line['period'] == 6-i and line['amount'] or 0 for i in range(7)]],
                #One of the entries in vals is the aml)id, which will let us load the account.move.line, as below, to extract the other information Ian wants.
                #self.env['account.move.line'].browse(aml_ids):
        return lines       


class report_account_aged_payableDMO(models.AbstractModel):
    _name = "account.aged.payabledmo"
    _description = "DMO Aged Payable"
    _inherit = "account.aged.payable"

    def _get_report_name(self):
        return _("DMO Aged Payable")


    def _get_columns_name(self, options):
        columns = super()._get_columns_name(options)
        for i, col in enumerate(columns):
            if col.get('name') == "Journal":
                columns[i] = {'name': "Invoice Date", 'class': 'date', 'style': 'white-space:nowrap;'}
            elif col.get('name') == "Account":
                columns[i] = {'name': "Ref", 'class': '', 'style': 'text-align:center; white-space:nowrap;'}
        return columns
        


    @api.model
    def _get_lines(self, options, line_id=None):
        lines = super()._get_lines(options, line_id)
        for vals in lines:
            if vals.get('level') == 4:
                aml_id = self.env['account.move.line'].browse(vals['id'])

                vals['columns'][1]['name'] = format_date(self.env, aml_id.move_id.invoice_date) #invoice date
                vals['columns'][2]['name'] = aml_id.move_id.ref #vendor reference  
                
                #From parent, this is:
                #'columns': [{'name': v} for v in [format_date(self.env, aml.date_maturity or aml.date), aml.journal_id.code, aml.account_id.display_name, format_date(self.env, aml.expected_pay_date)]] + [{'name': self.format_value(sign * v, blank_if_zero=True), 'no_format': sign * v} for v in [line['period'] == 6-i and line['amount'] or 0 for i in range(7)]],
                #One of the entries in vals is the aml)id, which will let us load the account.move.line, as below, to extract the other information Ian wants.
                #self.env['account.move.line'].browse(aml_ids):
        return lines        
