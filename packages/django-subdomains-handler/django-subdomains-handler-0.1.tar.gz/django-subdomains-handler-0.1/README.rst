=====
Django Lightweight Subdomains Handler
=====

This is a very short Django Middleware to handle each subdomains
with a specific URLconf file.

Example
-------

If you want to have something like::

	api.example.org
	
with a specific URLconf file for each of your subdomains

This what you're looking for!

Quick start
-----------

1. Add this on top of your MIDDLEWARE_CLASSES setting like this::

    MIDDLEWARE_CLASSES = (
        'django-subdomains-handler.subdomains.SubDomainMiddleware',
		...
    )

2. Add the SUBDOMAINS_URLCONF dict to your setting project file::

	SUBDOMAINS_URLCONF = {
		'api': 'api.urls',
	}

    Where 'api.urls' is your Django-app 'api' and urls is your urls.py module

3. Run your Django project and try to reach api.example.org
