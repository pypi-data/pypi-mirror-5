Version 0.5
=============
* During tests with Postgres, migration scripts failed. Fixed with a much cleaner
  way to check if table 'cmsplugin_text' exists.

Version 0.4
=============
* Fixed problem on
  manage.py dumpdata cmsplugin_text_wrapper
  which did not export any table content.
* Suppress nasty error messages, when table is created rather than migrated.

Version 0.3
=============
* Fixed the problem during migration, when table cmsplugin_text did not yet exists.

Version 0.2
=============
* On the page details view in the list of active plugins, the currently used wrapper is shown.

Version 0.1
=============

* Initial release to Pypi
