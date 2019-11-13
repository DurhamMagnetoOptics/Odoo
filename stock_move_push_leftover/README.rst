=========================
Stock Move Push Leftover
=========================

In Odoo 13, push rules are only applied to stock moves which
do not already have child moves.  The assumption is that, if 
a child move exists, this move is already accounted for by a
pull route, and so push rules are never applied.

This is true, but incomplete.  We can have cases where the
quantity in the current stock move exceeds the quantity
needed by the child moves.  This can happen if, for example,
an automatically generated PO is modified before being placed.

Odoo handles the case where the quantity is less than the
child needs (backorder) or when the quantity is greater than
the expected (todo) quanityt (extra move created to allow
push) but does not handle the case where the quanityt is as 
expected but more than the child needs.

This module fixes that.  When confirming a stock move and
checking whether pull rules need to be applied, we test
for child moves (same as stock Odoo) and if child moves exist
we calculate the total qty for which those move account.  If
this is less than the current move's quantity, we split off 
that leftover as a separate move, and apply push rules to
that new move.

==================
Known Limitations
==================

This does not apply in cases where the expected/reserved
quanity is increased after the move is committed/ready. So
it will not account for manually increasing the expected
quantity of a move; that should be done by increasing the
done quanity and letting existing logic take care of the 
extra.  This module is limited to the case where the quantity
is increased beyond the needs of the chained move _before_ the
move is committed.  This may be unique to the purchase module.

Note: demo data (from mts_else_mto) is, as setup, 
nearly but not quite sufficient for testing.  You
must first change the default location for the "Receipt"
operation to be "WH/Goods In".
