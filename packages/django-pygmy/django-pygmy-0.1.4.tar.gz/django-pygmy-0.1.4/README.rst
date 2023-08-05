django-pygmy
============

django-pygmy is a little app that colorizes source codez in your `Django <http://djangoproject.com/>`_ templates.

It uses `pygments <http://pygments.org/>`_ for prettify the codez and `django-classy-tags <https://github.com/ojii/django-classy-tags>`_ for easy-and-awesome creation of template tags.

.. image:: https://travis-ci.org/mattack108/django-pygmy.png
   :target: https://travis-ci.org/mattack108/django-pygmy

Installation
------------

To install ``django-pygmy``, simply run: ::

    pip install django-pygmy

Then add the app to your ``INSTALLED_APPS``: ::

    INSTALLED_APPS = (
        ...,
        'django_pygmy',
    )

Usage
-----

Render the awesomeness in your template: ::

    {% load pygmy %}

    {% pygmy object.code %}

It also takes the same options as `HtmlFormatter <http://pygments.org/docs/formatters/#htmlformatter>`_: class::

    {% pygmy object.code nowrap='True' linenos='table' %}

Lexers
------

By default ``django-pygmy`` tries to guess which lexer to use based on the provided code.

If you wish you can define any lexer of `Pygments lexers <http://pygments.org/docs/lexers/>`_ like so: ::

    {% pygmy object.code lexer='python' %}
