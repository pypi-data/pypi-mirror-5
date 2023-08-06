.. contents::

What does it do?
================

This Plone addon allows editors to control the visibility of portlet columns -
no matter if they are empty or contain portlets.

Editors can choose between:

* showing a column (even if it does not contain any portlets)

* hiding a column (even if it contains portlets)

* only show non-empty columns (standard Plone behaviour)



How does it work?
=================


`wm.showhidecolumns` uses infrastructure available in Plone 4:


the request variables ``disable_plone.rightcolumn`` and
``disable_plone.leftcolumn`` are used to control the column visibilty. (no
portletmanagers get overwritten or monkey-patched).

`archetypes.schemaextender` is used to make the settings available on all types
implementing ``wm.showhidecolumns.interfaces.IControlColumns``

`plone.browserlayer` is used to make sure the extra fields and the viewlet that
adds the request variables only show up if the product is installed.



How do I use it?
================


To allow control column visibilty on custom content types just make them
implement ``wm.showhidecolumns.interfaces.IControlColumns``.



How can I help?
===============

* Add translations for your language (currently English and German)

* Add support for Dexterity content types

* Add tests

* report bugs or request features in the `issue tracker`_

.. _`issue tracker`: https://github.com/webmeisterei/wm.showhidecolumns/issues  





