js.fanstatictools
*****************

Introduction
============

This library provides some javascript helpers for use with `fanstatic`_.

.. _`fanstatic`: http://fanstatic.org


Get URLs of resources from within Javascript
============================================

When you need to load other (fanstatic) resources inside your javascript, you
may want to calculate the URL to the fanstatic library the resource is defined
in. Using relative URLs does not work, because they are calculated relative to
the windows URL, not to the URL of the current script, which can be different.

After including the js.fanstatictools.lib_url fanstatic resource, you are able
to call fanstatictools.get_library_url('name_of_your_library'), which returns
the url. Add the filename of the resource to the end and you are done.
