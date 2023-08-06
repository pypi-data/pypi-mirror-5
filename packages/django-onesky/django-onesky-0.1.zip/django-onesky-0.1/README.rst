===============
django-onesky
===============

OneSky Inline Translation library for Django

See full documentation at http://www.oneskyapp.com

To wrap text string with <os-p> tag::

	trans('my string')

To wrap text string with special prefix and suffix::

	trans2('my string')


Installation
============

Install via ``pip``::

    $ pip install django-onesky


Setup
=====

1. Add ``onesky`` to INSTALLED_APPS in your django settings file.

    ::

        INSTALLED_APPS = (
            ...
            'onesky',
            ...
        )

