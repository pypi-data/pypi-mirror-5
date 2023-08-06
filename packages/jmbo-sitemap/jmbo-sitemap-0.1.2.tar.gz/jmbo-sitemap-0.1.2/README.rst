Jmbo Sitemap
============
**XML and HTML sitemap product for Jmbo.**

.. contents:: Contents
    :depth: 5

Installation
------------

#. Install or add ``jmbo-sitemap`` to your Python path.

#. Add ``jmbo_sitemap`` and ``django.contrib.sitemaps`` to your ``INSTALLED_APPS`` setting.

#. Add (r'^', include('jmbo_sitemap.urls')) to urlpatterns. You may need to add this early in the chain so other patterns don't take precedence.

