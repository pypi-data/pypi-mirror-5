============
django-tides
============

A tool to acquire, store, and serve tide data. Designed to have pluggable backends for multiple tide services. So far NOAA_ is the only source.

Installation
============

Use ``pip`` to install from PyPI::

	pip install django-tides

Add ``django_tides`` to your settings.py file::

	INSTALLED_APPS = (
	    ...
	    'django_tides',
	    ...
	)

Additional Requirements
=======================

``beautifulsoup4`` to parse the XML served by NOAA

``django-tastypie`` to generate the API

GeoDjango_ is used to store point data for tide stations. I use PostGIS_ as my database backend.

Acquiring Data
==============

``django-tides`` comes with a management function::

	./manage.py update_tides

This will pull all tide data for all available backends. Use this with care as it will use a lot of bandwidth.

Endpoints
=========

``django-tides`` exposes two endpoints for now:

/tides/api/water-level/
-----------------------

Provides the water level at a specific station over time. Example:

``/tides/api/water-level/?format=json&time__gte=2013-07-04%2000:00&time__lte=2013-07-15%2000:00&limit=10&station__source_id=8447355``

/tides/api/station/
-------------------

Provides a list of stations within proximity of a given point. Example:

``/tides/api/station/?format=json&limit=10&offset=0&lat=41.77873679916478&lon=-70.47317504882812``

Contributing
============

Think this needs something else? To contribute to ``django-tides`` create a fork on Bitbucket_. Clone your fork, make some changes, and submit a pull request.

Bugs are great contributions too! Feel free to add an issue on Bitbucket_.

.. _Bitbucket: https://bitbucket.org/bilgecode/django-tides
.. _GeoDjango: https://docs.djangoproject.com/en/dev/ref/contrib/gis/
.. _PostGis: http://postgis.net/
.. _NOAA: http://tidesandcurrents.noaa.gov/
