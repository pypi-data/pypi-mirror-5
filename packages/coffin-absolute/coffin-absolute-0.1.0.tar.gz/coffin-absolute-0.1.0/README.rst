coffin-absolute
===============
Provides ``absolute_url`` tag and filter in Jinja2 templates when using the ``coffin`` package with Django.

The ``absolute_url`` tag has the same arguments as the ``url`` tag.
The ``absolute_url`` filter takes the ``request`` as the additional, first argument.

Both the tag and the filter render an absolute url based on the host of the request context.

Installation
============
Just add ``'coffin_absolute'`` to ``INSTALLED_APPS``.
