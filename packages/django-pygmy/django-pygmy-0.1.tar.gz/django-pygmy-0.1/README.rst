django-pygmy
============

django-pygmy is a little app that colorizes source codez in your `Django <http://djangoproject.com/>`_ templates. It uses `pygments <http://pygments.org/>`_ for prettify the codez and `django-classy-tags <https://github.com/ojii/django-classy-tags>`_ for easy-and-awesome creation of template tags.

Installation
------------

To install ``django-pygmy``, simply run: ::

    pip install django-pygmy

And add the app to your ``INSTALLED_APPS``: ::

    INSTALLED_APPS = (
        ...,
        'django_pygmy',
    )

Usage
-----

Render the awesomeness in your template: ::

    {% load pygmy %}

    {{ obj.title }}

    {% pygmy obj.code %}
