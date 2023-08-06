stxnext.grayscale
=================

Introduction
============

The ``stxnext.grayscale`` package is an add-on Product for Plone that gives the possibility of displaying
the web content of the site in the grayscale colors.

.. image:: https://github.com/stxnext/stxnext.grayscale/raw/master/docs/stxnext.grayscale.example.png

Colors transformation
=====================

The images are transformed on-the-fly using the PIL library.

The css and html documents are transformed with regular expression to substitute the colors
definitions with their grayscale equivalent values.

In Plone 4 (with plone.resource package installed) the transformed resources (images, css files)
are cached in the file system to avoid multiple transformation of the same resource.

Installation
============

Plone 3
-------

For sites based on Plone 3.x use `stxnext.grayscale v 1.0.0`_

Plone 4
-------

1. Add stxnext.grayscale to your plone.recipe.zope2instance section's eggs.
Define the resources parameter to point to the existing directory where the
transformed resources will be stored to avoid multiple transformation of
the same resource::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    resources = ${buildout:directory}/var/resources
    ...
    eggs =
        ...
        stxnext.grayscale
        
2. Install the Product via portal_quickinstaller

Configuration
=============

In the stxnext.grayscale tool's control panel (/@@grayscale_settings) choose the Plone skins
to be transformed to grayscale colors.

Author & Contact
================

 * Radosław Jankiewicz ``radoslaw.jankiewicz@stxnext.pl``
 * Sebastian Kalinowski ``sebastian.kalinowski@stxnext.pl``

.. image:: http://stxnext.pl/open-source/files/stx-next-logo

**STX Next** Sp. z o.o.

http://stxnext.pl

info@stxnext.pl

License
=======

This package is licensed under the Zope Public License.

.. _`stxnext.grayscale v 1.0.0`: https://pypi.python.org/pypi/stxnext.grayscale/1.0.0
