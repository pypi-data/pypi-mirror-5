django-cms-autoblocks
=====================

Django-cms-autoblocks is an app that allows you to place arbitrary content blocks into your templates, so that you can take advantage of django-cms placeholders in the templates for your custom apps, without having to include django-cms as a requirement for your custom app (because the django-cms dependency is introduced at the template level by the template author).

Installation
=====================

From PyPi: ``pip install autoblocks``

From GitHub: ``pip install git+git@github.com:Strathcom/django-cms-autoblocks.git``

Setup
=====================

1. Add ``autoblocks`` to settings.INSTALLED_APPS.
2. Run ``manage.py syncdb``.
3. If you want to do frontend editing, add the dependencies for the django-cms toolbar to your templates.

Usage
=====================

In your template::

	{% load autoblocks_tags %}
	{% autoblock 'this is my auto block' %}
	{% autoblock 'this is' 'also' 'an autoblock' %}
	{% autoblock 'blurb-' model_instance.id %}
	{% autoblock 'blurb-' model_instance.id on site %}
	{% autoblock 'blurb-' model_instance.id on site as foo %}

The templatetag will generate an Autoblock with a placeholder field for you to work with tied to either the current site (``Site.objects.get_current()``), or the site instance you pass in when you use the ``{% autoblock ... on <site> %}`` variation of the tag.


Extras
=====================

If you add ``django.core.context_processors.request`` to ``settings.TEMPLATE_CONTEXT_PROCESSORS``, autoblocks will only be created when the page is accessed by an authenticated user with the ``autoblocks.add_autoblock`` permission.



Autoblocks - Roll Out!