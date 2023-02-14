==============================
DMO Accounting
==============================
13.0.1
Various tweaks to Odoo accounting to better match DMO's work flow.

Customer Invoice List View: Tax Excluded, Tax, Total, and Amount Due are also shown in local currency
Add option to Company settings to make 'Reference' field mandatory when creating vendor bills.

13.0.2
Adds total amount to vendor bill Group Payment view.

Adjusts column names and removes "memo" field from payment receipt document

13.1.0
New report style: "DMO Aged Payable/Receivable"

Registering Payment (from Bill view, from single Bill selected from list, and from multiple Bills selected from list) all open the same 'multipayment' wizard for registering payments (which jumps you to the Payment upon completion, instead of returning you to the Bill) 

When a Bill is opened from the aged partner report, it follows the normal default values when registering payment 

13.1.1
Added a shortcut button to related Payments from the Bill.
Removed the 'multipayment' override introduced in 13.1.0

16.0.0.0
All changes disabled, for upgrade to vanilla Odoo 16 for legacy transactional data only.




==================
Known Limitations
==================


==================
Version
==================
16.0.0.0
