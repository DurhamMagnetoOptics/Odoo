==================
MTS else Alternate
==================

This module adds a new procurement method, MTS_else_alt:
Take from stock; if shoftfall, trigger alternate rule

When there is sufficient stock, the MTS_else_alt rule is treated as MTS

When there is no stock, we trigger the alternate rule.

When there is some stock (but not enough), we execute two moves:
1) Take from stock as per the current rule for what is available
2) Execute the alternate rule for the shortfall.

This differs from the default MTS_else_MTO rule in that:
1) It allows partial fulfillment from stock
2) The MTO rule is a completely separate rule, rather than treating the MTS_else_MTO
    rule as MTO.  This means we can have a different source location for the MTO branch
    than we do for the MTS branch.

Essentially, we are recreating the functionality of the OCA module stock_mts_mto_rule
using the new architecture for mts_else_mto in Odoo 13