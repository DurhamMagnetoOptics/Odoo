==============================
Product Supplierinfo Round Up
==============================

Odoo 13 treats min_qty in supplierinfo as a condition of selecting
that supplier.  If we want less than min_qty it says this supplier
doesn't apply.

This module adds the option to use the designated supplierinfo, but
to increase the ordered quantity to match the min_qty.

This module also adds an Order Increment to the supplier info.  If 0.0
it is ignored.  Otherwise the quanity to order in an RFQ/PO is set to 
be above the MOQ and in increments of the Order Increment.

==================
Known Limitations
==================


