.. image:: https://secure.travis-ci.org/unice/unice.portlet.vimeo.png
   :target: https://travis-ci.org/unice/unice.portlet.vimeo

Introduction
============

This portlet shows a vimeo item as vimeo in the portlet.
It's LinguaPlone aware, and is initially created to provide a
language-dependent address footer.

Author: Lennart Regebro <regebro@gmail.com>

Development funded by the Nordic Council and Nordic Concil of Ministers.
http://www.norden.org/


Compatibility
=============

The product is compatible with Plone 3 and Plone 4.


Installing
==========

Add `unice.portlet.vimeo` to your buildout and re-run buildout.
Install the product in your Plone site using the Plone Control Panel
(`prefs_install_products_form`) or the ZMI's `portal_quickinstaller`.


Using
=====

Go to `@@manage-portlets`. If the product was installed properly, you'll have
the option to add a Vimeo Portlet.

Next, select a vimeo item to display. It can be any type of item. You can
select which of the item's fields you want to display in the portlet's vimeo
area:

* Title (either as a link to the vimeo item or as plain text)
* Description
* Date
* Body text
* Image

When the vimeo item doesn't have a selected field, it should work without
errors, but you'd obviously not see the field in the portlet.

You can set these options separately:

* portlet's title as shown in `@@manage-portlets` screen
* portlet header title as rendered on page
  (use vimeo's title or select custom)
* hide portlet header altogether
* conditionally show a portlet footer with a link to the vimeo item
  (link text is configurable)
* disable the portlet border

