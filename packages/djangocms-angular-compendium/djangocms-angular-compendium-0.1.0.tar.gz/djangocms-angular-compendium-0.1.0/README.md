djangocms-angular-compendium
============================

A collection of templates to be used for overriding existing templates from various DjangoCMS
plugins, when running with the AngularJS framework.

Currently these templates are overridden:

* ``cmsplugin_filer_image/image.html``: Replace tag ``<img src="...">`` against ``<img ng-src="...">``.
  This is required by the AngularJS [ngSrc](http://docs.angularjs.org/api/ng.directive:ngSrc)
  directive.
* ``cms/plugins/bootstrap/carousel.html`` and ``carousel-slide.html``: Replace the Carousel HTML
  code with a variant running with the [Angular UI Bootstrap](http://angular-ui.github.io/bootstrap/#/carousel)
  library.

Installation and configuration
------------
From PyPI::

	pip install djangocms-angular-compendium

In your project's settings, add ``angularjs_compendium`` to ``INSTALLED_APPS``. Check that this
entry is located before any DjangoCMS plugin entry::

	INSTALLED_APPS = (
	    ...
	    'angularjs_compendium',
	    ...other DjangoCMS plugins
	    ...
	)

License
-------
Released under the terms of MIT License.

Copyright (C) 2013, Jacob Rief <jacob.rief@gmail.com>
