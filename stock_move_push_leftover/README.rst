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

In addition, 'merge_procure_method' and 'merge_created_PO' on
the operation type allow to merge stock moves even when
procurement_method and created_purchase_line_id and 
purchase_line_id, respectively, do not match.  This is necessary
to allow for the case where a rounded-up purchase is requested by
a re-ordering rule.  In that case, the destination of the
next pull move in the sequence (the originating pull) and the
destination of the 'leftovers' caught by the push rull are the
same, but Odoo does not merge them because one is make_to_stock
while one is make_to_order (which is a heck of thing to attach to
a pull rule when the source was a generic reordering rule, Odoo!)
and one has the creating PO attached and one does not.  It makes 
sense to receive goods based on PO line, but once they are all 
in stock, we consider them fungible and shouldn't make separate
moves just becuase some came from non-alloated stock and some 
were purchased explicitely against a particular MO.

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
