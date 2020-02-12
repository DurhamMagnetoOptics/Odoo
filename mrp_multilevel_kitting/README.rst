==============================
Multi-level Kitting
==============================

Add "Bin Name" property to BOM line.

When the manufacutring operation is kicked off for a BOM, (assuming "Multilevel Kitting"
flag is set on the Manufacturing opration and the BOM) source location
for each move is set to a sublocation of the MOs source, whose name mathces the "bin name."
This location is created if it doesn't already exist.

13.0-13.3 Change:
Bin name is now done line-by-line rather than BOM-by-BOM.  This means we do not have to make
each bin into its own Odoo product. We reserve prodcut 'status' for true subassemblies, and 
treat bins as purely locations.

==================
Known Limitations
==================

If an MO is cancelled, the locations are not removed.