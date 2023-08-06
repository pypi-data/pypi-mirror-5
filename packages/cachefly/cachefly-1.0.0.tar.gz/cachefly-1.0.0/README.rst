cachefly -- convenient CacheFly CDN management
==============================================

The CacheFly CDN exposes an HTTP based API for forcefully purging content from their reverse proxying CDN solution. The ``cachefly`` module provides a simple interface for performing those actions.

Furthermore, the ``django_cachefly`` module provides a convient way to configure and access an application wide API client instance through your Django settings.


Installation
------------

To install ``cachefly`` and ``django_cachefly``, do yourself a favor and don't use anything other than `pip <http://www.pip-installer.org/>`_:

.. code-block:: bash

    $ pip install cachefly


Installation in Django
----------------------

After the module has been installed, you need to add ``django_cachefly`` to your list of ``INSTALLED_APPS`` in your application configuration:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_cachefly',
    )

You also need to configure your CacheFly API key in your application's settings file:

.. code-block:: python

    CACHEFLY_API_KEY = '..'

The CacheFly API client can now be easily accessed from the entire application:

.. code-block:: python

    from django_cachefly import client
    
    ...


Testing
-------

Testing requires a set of valid credentials. All tests are performed against URLs in the ``/_testing`` path for the CDN node your select. Credentials are loaded from the environment during testing for security:

``CACHEFLY_API_KEY``
    API key to use for testing.
