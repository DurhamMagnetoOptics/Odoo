# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from odoo.tools import float_compare

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    ##TODO: add a contraint to make sure this matches the product.  Ideally the drop down would only display valid ones,
    # and maybe even nothing until the product is set.  Can it autopopulate when product is chosen?
    # We ought to be able to steal all of that functionality from the Manufacturing Order view.
    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        ('type', '=', 'normal')]""",
        check_company=True,
        help="Bill of Materials allow you to record the materials used to produce this lot.")

    #We don't really care about template, but having it available (and automatically tracking the selected product) means 
    #we can do some nice things on the form with limiting the BOMs that are available for selection
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id')


    @api.onchange('product_id', 'company_id')
    def onchange_product_id(self):
        """ Finds BoM of changed product. """
        if self.product_id and self.product_id.link_BOM_to_lot:  #only make changes if the boolean is set, otherwise we leave BOM untouched.  This means in cases where we chose a product where it was set (and the BOM was automatcially set) then deleted the product, the BOM is left.  That's safer than deleting it when the flag wasn't set.
            if not self.bom_id or (self.bom_id.product_id != self.product_id) and (self.bom_id.product_tmpl_id != self.product_tmpl_id): #If we match the product, leave the BOM as-is, because it's valid and if it came through from the MO it should have priory over whatever the default BOM is
                ##If we no longer match the product, then we go ahead and overwrite whatever was selected
                bom = self.env['mrp.bom']._bom_find(product=self.product_id, company_id=self.company_id.id, bom_type='normal')
                if bom:
                    self.bom_id = bom
                else:
                    self.bom_id = False
    