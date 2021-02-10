==============================
DMO Accounting
==============================

Various tweaks to Odoo accounting to better match DMO's work flow.

Customer Invoice List View: Tax Excluded, Tax, Total, and Amount Due are also shown in local currency

==================
Known Limitations
==================
Vendor Bill creation: would like Reference to be a required field. Doing that in a module means either making
it dependent on a setting somwhere, or failing unit tests where Odoo hasn't provided a reference in their test data.
Better, therefore, to do that through the developer mode UI: View Fields, select the field, tick Required.  the
functionality has been commented out of this module, but left as a reminder.