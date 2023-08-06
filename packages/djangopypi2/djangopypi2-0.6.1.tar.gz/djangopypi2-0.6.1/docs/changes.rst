History
=======
0.6.1 (2013-04-??)
------------------
* Apache+mod_wsgi documentation (thanks Julien Rottenberg <julien@rottenberg.info>)

0.6.0 (2013-04-28)
------------------
* Upgrade to Twitter Bootstrap 2.3.1
* Django 1.5 compatibility
* Added 'delete' button to package and release
* Added missing links to internal pages
* Remove useless "empty" operations like editing a package

0.5.9 (2013-04-14)
------------------
* Require Django 1.4.5; 1.5 is not yet supported

0.5.8 (2013-03-05)
------------------
* Fix supervisor config so 'environment' works (thanks Toby Champion)
* Distribution deletion now removes the underlying files (thanks Edward Easton)
* Added ALLOW_VERSION_OVERWRITE user config (thanks Edward Easton)

0.5.7 (2012-11-15)
------------------
* Fix broken ``admin`` link
* When a package name contains a '-' sign, try to redirect to an equivalent one with '_' in the name if it's not found

0.5.6.1 (2012-10-23)
--------------------
* Fix ~/.djangopypi2 to expand according to os.environ['USER'] (thanks davedash)
* Support for DJANGOPYPI2_ROOT environment variable, for explicit project root

0.5.6 (2012-10-10)
------------------
* Fix DOAP views and add links to them from package and release views
* Add pypi_manage app

0.5.5 (2012-10-08)
------------------
* New pypi_metadata app, holds only package metadata
* /simple/ interface is case insensitive
* New pypi_packages app, split out of pypi_frontend, doing only package management
* From now on pypi_frontend only implements scripting interfaces (xmlrpc, distutils, doap)
* Removed pypi_config app
* Add missing TEMPLATE_CONTEXT_PROCESSORS to website.settings
* Add pypi_users for showing user profiles
* Add Shpinx docs

0.5.4 (2012-10-05)
------------------
* Allow additional settings in ~/.djangopypi2/settings.py
* Fix bug in distutils' upload causing upload to fail
* Fix bug causing uploaded files to be saved with the wrong name

0.5.3.1 (2012-10-04)
--------------------
* Fix mirroring not handling ``simple`` method

0.5.3 (2012-10-04)
------------------
* Remove policy from MirrorSite
* Redirect to first enabled mirror site when package is not found locally

0.5.2 (2010-10-03)
------------------
* Organize code in distutils views
* Detect binary platform (in case of bdist_*) from filename

0.5.1 (2012-10-03)
------------------
* Provide ready-to-deploy Django project within the package

0.5.0 (2012-10-03)
------------------
* Removed south support (too many changes), hopefully added in a future version
* Added bootstrap-based user interface
* Split djangopypi to several Django apps
* Switched to relative imports
* All configuration resides in the database and editable from the admin
* Static files are automatically served when DEBUG = True
* Removed loadclassifiers command
* Contains fixtures with initial data for all configuration models

0.4.4 (2012-04-18)
------------------

* xmlrpc bug fixes
* CSRF token template tags on forms
* Transaction bug fixes
* Switched to logging over stdout
* Proxy simple and detail views when necessary
* Removed unused legacy view, submit_package_or_release
* ppadd management command working again

0.4.3 (2011-02-22)
------------------

* Moved xmlrpc views into views folder
* Moved xmlrpc command settings to the settings file
* Cleaned up xmlrpc views to remove django.contrib.sites dependency

0.4.2 (2011-02-21)
------------------

* Added CSRF support for Django>=1.2
* Added conditional support to proxy packages not indexed

0.4.1 (2010-06-17)
------------------

* Added conditional support for django-haystack searching

0.4 (2010-06-14)
----------------

* 'list_classifiers' action handler
* Issue #3: decorators imports incompatible with Django 1.0, 1.1
* RSS support for release index, packages
* Distribution uploads (files for releases)

0.3.1 (2010-06-09)
------------------

* Installation bugfix

0.3 (2010-06-09)
----------------

* Added DOAP views of packages and releases
* Splitting djangopypi off of chishop
* Switched most views to using django generic views

Backwards incompatible changes
______________________________

* Refactored package/project model to support multiple owners/maintainers
* Refactored release to match the metadata only that exists on pypi.python.org
* Created a Distribution model for distribution files on a release

0.2.0 (2009-03-22)
------------------

* Registering projects and uploading releases now requires authentication.
* Every project now has an owner, so only the user registering the project can 
  add releases.
* md5sum is now properly listed in the release link.
* Project names can now have dots ('.') in them.
* Fixed a bug where filenames was mangled if the distribution file already existed.
* Releases now list both project name and version, instead of just version in the admin interface.
* Added a sample buildout.cfg. Thanks to Rune Halvorsen (runeh@opera.com).

Backwards incompatible changes
______________________________

* Projects now has an associated owner, so old projects must be exported and 
  imported to a new database.

0.1.0 (2009-03-22)
------------------

* Initial release
