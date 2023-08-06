Changelog
=========

0.2.1 - 2013-10-24
------------------

* Packaging fixes; this is done for wording and cleaner generic setup
  integration.

0.2 - 2013-07-09
----------------

* Now provide the customized ploneform macros, migrated in from the
  pmr2.app module.
* Making use of bootstrap classes
* Removed deprecated zope.app.* imports.

0.1 - 2013-01-17
----------------

* Initial release of various helper forms and view classes for the pmr2
  libraries.
* Provide a wrapped BrowserView class that can adapt to multiple wrapper
  templates much like how plone.z3cform does, so that views don't invoke
  items that may not be available due to lack of a full portal.
