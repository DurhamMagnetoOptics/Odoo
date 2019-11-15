=========================
MRP Apply Parent Pull
=========================

Normally, when looking for a rule to satisfy a procurement, Odoo looks
for rules that apply to the locations above the destination location
as well.  That is, if I have a pull rule from Stores -> Builds, and 
create a need in Builds/Hust, that rule will be triggered and parts
will be pulled from Stores -> Builds/Hust.

However, the MRP module always initially creates it's procurements as
mts and then runs _adjust_procure_method to look for any pull rules that
might apply, and sets those moves to mto instead (effectively applying
the rule).  Unlike in the normal application, this only looks for rules
that apply to the source location, not it's parents.  So a MRP-generated
need in Builds/Hust does not have any rule to satisfy it, and it remains
as mts.

This module corrects that behaviour.

==================
Known Limitations
==================


