.. contents::

Introduction
============

raptus.article.accordion provides an accordion listing for Articles.

The following features for raptus.article are provided by this package:

Components
----------
    * Accordion

Dependencies
------------
    * raptus.article.core
    * raptus.article.nesting

Installation
============

To install raptus.article.accordion into your Plone instance, locate the file
buildout.cfg in the root of your Plone instance directory on the file system,
and open it in a text editor.

Add the actual raptus.article.accordion add-on to the "eggs" section of
buildout.cfg. Look for the section that looks like this::

    eggs =
        Plone

This section might have additional lines if you have other add-ons already
installed. Just add the raptus.article.accordeon on a separate line, like this::

    eggs =
        Plone
        raptus.article.accordion

Note that you have to run buildout like this::

    $ bin/buildout

Then go to the "Add-ons" control panel in Plone as an administrator, and
install or reinstall the "raptus.article.default" product.

Note that if you do not use the raptus.article.default package you have to
include the zcml of raptus.article.accordion either by adding it
to the zcml list in your buildout or by including it in another package's
configure.zcml.

Copyright and credits
=====================

raptus.article is copyrighted by `Raptus AG <http://raptus.com>`_ and licensed under the GPL. 
See LICENSE.txt for details.
