==============================
Stock Auto Transfer
==============================

1. Creates a new "ephemeral" option for Operation Types.  

2. Creates a routine to automatically generate moves to clear a location of surplus stock, and assigns them.

3. Creates a routine to automatically generate procurements to satisfy all stock shortfalls in a location.

4. Creates a routine to automatically unreserve unstarted "ephemeral" moves from a target location, containing target products

5. Creates a routine to automatically assign all moves from a target location, containing target products.

This enables the following flow:
In place of the normal stock scheduler: run (4) for all locations/products, then run (3) for all locations/products, then run the normal stock scheduler, then run (2) for all locations.
In addition, to prevent having to constantly run the scheduler, we add an extra trigger:
Optionally, upon validation of an operation into a location, run 4 then 5 then 2 for that location/products.

TODO: Adds "Auto Fulfill" and "Auto Empty" buttons to locations.  Adds "Cancel All" to Operation Type.

==================
Known Limitations
==================

3. Is effectively the same as setting 0/0/1 re-ordering rules for every relevant location, for every product.  But it is inferior in that
it won't take into account products that are on the PO but not yet confirmed as ordered and due in.  Therefore this option should only be
used in conjuction with routes that generate Transfers, and not routes that generate Buys.

5. Is very similar to https://odoo-community.org/shop/product/stock-move-auto-assign-5414#attr=8281, but withouot the job queue to collate
duplicate results, we run it at the picking level instead, so that it's not constantly executing.
