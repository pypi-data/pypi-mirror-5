Introduction
============

Extends the article by a second WYSIWYG text field to make it possible to split your text 
into two parts and display it for example above and below another component.

The following features for raptus.article are provided by this package:

Fields
------
    * Additional WYSIWYG text field for the articles.

Components
----------
    * Additional text (displays your text above an image or a video)
    * Additional text left (displays your text in a separate column on the left)
    * Additional text right (displays your text in a separate column on the right)

Dependencies
------------
    * archetypes.schemaextender
    * raptus.article.core

Installation
============

To install raptus.article.additionalwysiwyg into your Plone instance, locate the file
buildout.cfg in the root of your Plone instance directory on the file system,
and open it in a text editor.

Add the actual raptus.article.additionalwysiwyg add-on to the "eggs" section of
buildout.cfg. Look for the section that looks like this::

    eggs =
        Plone

This section might have additional lines if you have other add-ons already
installed. Just add the raptus.article.additionalwysiwyg on a separate line, like this::

    eggs =
        Plone
        raptus.article.additionalwysiwyg

Note that you have to run buildout like this::

    $ bin/buildout

Then go to the "Add-ons" control panel in Plone as an administrator, and
install or reinstall the "raptus.article.default" product.

Note that if you do not use the raptus.article.default package you have to
include the zcml of raptus.article.additionalwysiwyg either by adding it
to the zcml list in your buildout or by including it in another package's
configure.zcml.

Usage
=====

Add/Edit your article
---------------------
If you add or edit an article you get a new rich text field called additional text.
Insert the text you would like to have displayed by the additional wysiwyg component
and press save.

Components
----------
Navigate to the "Components" tab of your article and select one of the additional
wysiwyg components and press "save and view".

Copyright and credits
=====================

raptus.article is copyrighted by `Raptus AG <http://raptus.com>`_ and licensed under the GPL. 
See LICENSE.txt for details.
