=========================
DMO Demo Data
=========================

For manual testing (and unit testing) we often want data that takes advantage
of several of our modules at once.  In order not to add unecessary dependencies
between our modules, we have this one test module that wraps up all of the
dependencies and is therefore a very good place to put all of our demo data
and test flows since it can describe the full flow instead of just a piece of it.

This also provides a handy way to install one module and get all of them loaded.

==================
Known Limitations
==================

No one else will make any sense of it.
