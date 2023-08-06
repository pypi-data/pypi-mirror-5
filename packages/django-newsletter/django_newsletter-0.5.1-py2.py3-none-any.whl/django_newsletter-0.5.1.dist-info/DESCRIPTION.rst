=================
django-newsletter
=================

.. image:: https://badge.fury.io/py/django-newsletter.png
    :target: http://badge.fury.io/py/django-newsletter

.. image:: https://secure.travis-ci.org/dokterbob/django-newsletter.png?branch=master
    :target: http://travis-ci.org/dokterbob/django-newsletter

.. image:: https://pypip.in/d/django-newsletter/badge.png
        :target: https://crate.io/packages/django-newsletter?version=latest

Newsletter application for the Django web framework.
----------------------------------------------------

What is it?
===========
Django app for managing multiple mass-mailing lists with both plaintext as
well as HTML templates with rich text widget  integration, images and a smart
queueing system all right from the admin interface.

Status
======
We are currently using this package in several large to medium scale production
environments, but it should be considered a permanent work in progress.

Documentation
=============
Extended documentation is available on
`Read the Docs <http://django-newsletter.readthedocs.org/>`_.

Translations
============
Most if not all strings are available in Dutch, German, French, Farsi,
Russian and English. Contributions to translations are welcome through
`Transifex <http://www.transifex.net/projects/p/django-newsletter/>`_.

.. image:: https://www.transifex.com/projects/p/django-newsletter/resource/django/chart/image_png
    :target: http://www.transifex.net/projects/p/django-newsletter/

Compatibility
=============
Currently, django-newsletter is being tested to run on Python 2.6, 2.7 and the
latest Django 1.4 and 1.5 releases. Apart from tests it *should* be compatible
with Python 2.5 as well.

Requirements
============
Please refer to `requirements.txt <http://github.com/dokterbob/django-newsletter/blob/master/requirements.txt>`_
for an updated list of required packages.

Tests
==========
Fairly extensive tests are available for internal frameworks, web
(un)subscription and mail sending. Sending a newsletter to large groups of recipients
(+15k) has been confirmed to work in multiple production environments. Tests
for pull req's and the master branch are automatically run through
`Travis CI <http://travis-ci.org/dokterbob/django-newsletter>`_.

Feedback
========
If you find any bugs or have feature request for django-newsletter, don't hesitate to
open up an issue on `GitHub <https://github.com/dokterbob/django-newsletter/issues>`_
(but please make sure your issue hasn't been noticed before, finding duplicates is a
waste of time). When modifying or adding features to django-newsletter in a fork, be
sure to let me know what you're building and how you're building it. That way we can
coordinate whether, when and how it will end up in the main fork and (eventually) an
official release.

In general: thanks for the support, feedback, patches and code that's been flowing in
over the years! Django has a truly great community. <3

License
=======
This application is released
under the GNU Affero General Public License version 3.


Changes
=======

0.5.1 (15-11-2013)
------------------

- Added Italian translation, thanks to azanibellato.
- Support for pluggable/custom user models (#101).
- Proper Sphinx documentation with autodoc on Read the Docs (#90).
- Compatibility with Django 1.6 thanks to @jnss (#97).
- Include default message templates in package (#95).
- Fix database to template file migration for non-ASCII characters (#94).
- Fix small issues with vCard imports (mainly mimetype-related).

0.5 (03-10-2013)
----------------

- Added proxy for app-specific settings.
- Optional skipping of email confirmation in views (`CONFIRM_EMAIL_<ACTION>`).
- Russian translation (contributed by ak3n).
- Added explicit HTML toogle to Newsletter model.
- Fix JavaScript submit link on "Add submission", ported to use jQuery.
- Replacement of remaining function based views with class based equivalents.
- Move message templates from database to files.

0.4.1 (15-04-2013)
------------------

- Started keeping a decent history file. (Finally...)
- Support Django 1.5; make use of class based generic views
- Drop Django 1.3 and Python 2.5 support.
- 100% test coverage for views
- Farsi translations (contributed by rohamn)
- French translations (contributed by smalter)
- Admin actions for subscribing/unsubscribing (contributed by jnns)
- Introduced django-webtest for some tests
- Exempt previews from XFrame protection (fixes #54)

0.4 (20-11-2012)
----------------

- Major code cleanup; PEP8, imports, restructuring, removal of legacy code
- Improved testing throgh Travis and better test coverage
- South migrations
- Added German translation (contributed by jnns)
- WYSIWYG editor is now optional and pluggable, Imperavi and TinyMCE supported
- Timezone-aware date-times when Django 1.4 is used
- Ue of Django 1.3's messages framework
- Many small bugfixes (see GitHub issues)
- Drop support for Django 1.2
- Automatic detection of charset, encoding and dialect for CSV import
- Much cleaner log messages with proper message substitution
- Use Django's staticfiles contrib for static assets in admin interface
- Use surlex for more readable URL templates
- Use sorl-thumbnail for article images and default templates


