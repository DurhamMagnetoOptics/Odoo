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

    1) It allows partial fulfillment from stock instead of leaving the insufficient
    stock in place and ordering the full quantity

    2) The MTO rule is a completely separate rule, rather than treating the MTS_else_MTO
    rule as MTO.  This means we can have a different source location for the MTO branch
    than we do for the MTS branch (ie if there isn't stock in a storage location, then
    resupply/manufacutre in place instead of in the storge location). This is useful in
    JIT manufacturing flow, where goods in go direct to assembly stations and don't first
    flow through general store locations.

Essentially, we are recreating the functionality of the OCA module stock_mts_mto_rule
using the new architecture for mts_else_mto in Odoo 13

Changelog: 13.0.2: alternate rule is implemented as 'branch' action rather than 'mts_else_alt'
procurement method.  And the alternate rule is "_run_[action]" rather than being used directly
to calculate move values.  This allows the alternate rule to be manufacture, buy, etc., and 
not just MTO pull.

==================
Known Limitations
==================

The implementing of the alternate rule is not recursive.  This means the alternate rule
needs to be an atomic one (push or pull).  If the alternate rule is another mts_else_alt,
or an mts_else_mto, or probably any other custom one, it will fail.

This rule may disrupt the ability of mts_else_alt rules to predict in advance what
stock levels would be like (becuase this rule is run on demand but mts_else_alt precaches
all the moves before deciding what to do).  If you need mts_else_mto on the same route as
mts_else_alt, it's better to implement even the mts_else_mto as mts_else_alt where the
alternate rule is a simple MTS rule.  This trades speed for flexibility.
