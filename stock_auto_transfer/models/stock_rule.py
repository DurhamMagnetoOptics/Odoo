from odoo import api, models, fields

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        self.env['stock.move'].run_unreserve_ephemeral()
        if use_new_cursor:
            self._cr.commit()

        self.env['stock.location'].search([('auto_fulfill','=',True)]).run_auto_fulfill()
        if use_new_cursor:
            self._cr.commit()

        res = super()._run_scheduler_tasks(use_new_cursor, company_id)

        self.env['stock.location'].search([('auto_empty','=',True)]).run_auto_empty()
        if use_new_cursor:
            self._cr.commit()

        return res