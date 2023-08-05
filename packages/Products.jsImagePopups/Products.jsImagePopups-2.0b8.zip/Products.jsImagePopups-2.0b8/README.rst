Introduction
============

Products.jsImagePopups provides a jQuery lightbox plugin to open
image popups without using a new browser window.

By default links pointing to *image_view_fullscreen*, having a *rel*
attribute beginning with *lightbox* or contained in an element with
class *photoAlbumEntry* are using the provided plugin. This includes
the *news item* view the *album* view and the *image* of plone.

To activate the plugin for your own view either set the *rel* attribute
on the desired links or instantiate the links on your own, for an example
on how to do this have a look at the *browser/lightbox.init.js* file.

Changing the behaviour of the lightbox may be done by changing the *jsImagePopups*
property in the *site_properties* property sheet or by activating the
plugin by yourself and providing a custom settings object.
