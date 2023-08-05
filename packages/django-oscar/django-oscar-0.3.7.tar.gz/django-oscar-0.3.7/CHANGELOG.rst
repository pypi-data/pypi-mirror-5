=========
Changelog
=========

0.3.7 - 2013-07-03
------------------
* Extend number of years in bankcard expiry field

0.3.6 - 2013-04-08
-------------------
* Fix line-handling bug in order dashboard.

0.3.5 - 2012-09-28
------------------
A couple of minor adjustments for Tangent projects

* Add handling of custom redirect after adding to basket
* Add recursive URL decoration

0.3.4 - 2012-09-24
------------------

* Rework price lookups in offer calculations (backport of functionality from 0.4)
* Add additional block to profile template

Diff: https://github.com/tangentlabs/django-oscar/compare/0.3.3...0.3.4

0.3.3 - 2012-08-24
-------------------

* Minor bug fixes around category editing and order history.

0.3.2 - 2012-08-13
------------------

* Bug fix for basket calculations.
* Bug fix for absolute discount benefit calculations.

0.3.1 - 2012-08-08
------------------

* Now including the translation files.

0.3 - 2012-08-08
----------------

* i18n support added - Oscar now ships with .po files for seven languages.
  Translation files are welcome.
* Category management added to dashboard
* Some improvements to how group/variant products are handled
* Improved installation process using makefile

Migrations
~~~~~~~~~~

There are 3 new migrations in the catalogue app.  If you have a local version,
you will need to run::

    ./manage.py schemamigration catalogue --auto

to pick up the changes in Oscar's catalogue app.

Breaking changes
~~~~~~~~~~~~~~~~

A new setting ``OSCAR_MAIN_TEMPLATE_DIR`` has been introduced
as the template structure has been altered.  This requires your
``TEMPLATE_DIRS`` setting to be altered to include this folder, eg::

    from oscar import OSCAR_MAIN_TEMPLATE_DIR
    TEMPLATE_DIRS = (
        location('templates'),
        OSCAR_MAIN_TEMPLATE_DIR
    )

If you want to extend one of Oscar's templates, then use::

    # base.html
    {% extends 'oscar/base.html' %}

instead of::

    # base.html
    {% extends 'templates/base.html' %}


0.2.1 - 09 July 2012
--------------------

Mainly small bug-fixes to templates and javascript.  

0.2 - 01 June 2012
------------------

Many components have been rewritten since 0.1 - Oscar is much more of a complete
package now.  New features include:

* Dashboard for managing catalogue, offers, stock, vouchers and more.  This includes
  statistics pages to track performance.

* Sample templates, CSS and JS to get a shop up and running in a minutes.  

* Updated documentation.

* Reworking of shipping methods.

* Automatic up-selling on the basket page.  We now inform the user if they
  partially qualify for an offer.

The documentation still needs more work which we'll do over the next week or
two.

0.1
---

* Initial release - used in production by two major applications at Tangent but
  still quite rough around the edges.  Many features were implemented directly
  in the applications rather than using a feature from oscar.

* Docs are a bit stale and need updating in 0.2

