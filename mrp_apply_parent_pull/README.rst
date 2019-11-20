=========================
MRP Apply Parent Pull
=========================

Normally, when looking for a rule to satisfy a procurement, Odoo looks
for rules that apply to the locations above the destination location
as well (that is, a rule applies to it's destination location and its 
destination location's children).  With a pull rule from Stores -> Builds, 
a need in Builds/Hust  will be triggered and parts will be pulled from
Stores -> Builds/Hust.

However, the MRP module always initially creates it's procurements as
mts and then runs _adjust_procure_method to look for any pull rules that
might apply, and sets those moves to mto instead (effectively applying
the rule).  This means it is looking for a rule whose source is the raw
materials location and whose destination is virtual/produciton.  This means
the stock move will only be converted to MTO if there is a rule with the raw
material location as its exact source.  A rule that pulls from virt/prod -> Builds
will not convert a stock move from Builds/HUST -> virt/prod.  Only a a rule 
that pulls from Builds/HUST -> virt/prod will do that.

This module changes that behaviour, so that a single pull rule (e.g. Bulds -> 
virt/prod) will convert an MO-generated stock move from Builds or any child -> 
virt/prod from MTS into MTO.

==================
Known Limitations
==================

I can only find _adjust_procure_method used in the MRP module.  If it ends up being
called from other places, this will impact those too.  In that case we'll have to 
make a change and set a value in context from the two places in MRP we want to use it.

If there are multiple rules that match in the ancestry, it's not clear which one 
will be returned.
