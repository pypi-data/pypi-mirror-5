Django sencha
=============


Requirements
------------

`Django <https://www.djangoproject.com/>`_ 1.5 or later


Installation
------------

::

    $ pip install django-sencha


Setup
-----

Just add ``'sencha'`` to INSTALLED_APPS in
your settings.py::

    INSTALLED_APPS = (
        # ...
        
        'sencha',

        # ...
    )

Refer to Django `static files <https://docs.djangoproject.com/en/dev/howto/static-files/>`_
documentation to configure and deploy static files.


Usage
-----

You can refer to sencha in your template with::

    {{ STATIC_URL }}sencha/<static_file_name>
