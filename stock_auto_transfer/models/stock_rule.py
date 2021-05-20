from odoo import api, models, fields

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        found = self.env['stock.move'].run_unreserve_ephemeral()
        if found and use_new_cursor:
            self._cr.commit()

        locs = self.env['stock.location'].search([('auto_fulfill','=',True)])
        locs.run_auto_fulfill()
        if locs and use_new_cursor:
            self._cr.commit()

        res = super()._run_scheduler_tasks(use_new_cursor, company_id)

        locs = self.env['stock.location'].search([('auto_empty','=',True)])
        locs.run_auto_empty()
        if locs and use_new_cursor:
            self._cr.commit()

        return res