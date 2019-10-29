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
    than we do for the MTS branch (ie if there isn't stock in a storage location, then
    resupply/manufacutre in place instead of in the storge location). This is useful in
    JIT manufacturing flow, where goods in go direct to assembly stations and don't first
    flow through general store locations.

Essentially, we are recreating the functionality of the OCA module stock_mts_mto_rule
using the new architecture for mts_else_mto in Odoo 13


==================
Known Limitations
==================

The implementing of the alternate rule is not recursive.  This means the alternate rule
needs to be an atomic one (push or pull).  If the alternate rule is another mts_else_alt,
or an mts_else_mto, or probably any other custom one, it will fail.