Introduction
============

``ftw.footer`` provides a viewlet, which shows 1 - 4 contextual portlet columns.


Installation
============


- Add ``ftw.footer`` to your buildout configuration:

::

    [instance]
    eggs +=
        ftw.footer

- Run `bin/buildout`

- Install the generic import profile.


Configuration
=============

The amount of portlet columns in the footer can be configured in the
`portal_registry` option `IFooterSettings.columns_count`.

Up to four columns are currently supported.


Screenshot
===========

.. image:: docs/screenshot.png

The screenshot is created with
`plonetheme.onegov <https://github.com/OneGov/plonetheme.onegov>`_.



Links
=====

- Github project repository: https://github.com/4teamwork/ftw.footer
- Issue tracker: https://github.com/4teamwork/ftw.footer/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.footer
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.footer


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.footer`` is licensed under GNU General Public License, version 2.
