Django-Misaka
-------------

Now this app only provide filter, the tag and Misaka API will soon.

Installation
------------

1) Install from PyPI::

    pip install django-misaka

2) Add ``django_misaka`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'django_misaka',
    )

Usage
-----

In your template::

    {% load markdown %}
    ...
    {{ text|markdown|safe }}

