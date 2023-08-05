Introduction
============

raptus.header provides a folderish content type called Header which may
contain multiple images. The first image contained in the header folder
will be displayed by the header viewlet. If no header folder is found in
the current context the viewlet tries to find one in the acquisition chain.


Plone 3 compatibility
---------------------

This packages requires plone.app.imaging which requires two pins in buildout
when using Plone 3, which there are::

    Products.Archetypes = 1.5.16
    plone.scale = 1.2
