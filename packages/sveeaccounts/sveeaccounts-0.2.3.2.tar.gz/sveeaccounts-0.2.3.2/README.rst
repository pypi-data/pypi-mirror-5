.. _autobreadcrumbs: http://pypi.python.org/pypi/autobreadcrumbs
.. _Django: https://www.djangoproject.com/
.. _django-braces: https://github.com/sveetch/django-braces
.. _django-crispy-forms: https://github.com/maraujop/django-crispy-forms
.. _django-simple-captcha: https://github.com/mbi/django-simple-captcha
.. _django-registration: http://pypi.python.org/pypi/django-registration
.. _Pillow: https://pypi.python.org/pypi/Pillow

Introduction
============

**Sveetchies-account** is a `Django`_ application to embed all the registration stuff using 
`django-registration`_ and `django-simple-captcha`_.

This is not really intended to be a generic app, so use it at your own risk.

Actually this is just an implementation of an inherited `django-registration`_ backend with 
`django-simple-captcha`_ usage and with a `UserProfileBase` abstract model (and his 
form, and his form view) that can be used as a base for user profiles.

A ``REGISTRATION_BLOCKED`` optionnal variable can be added in settings, if at ``True`` 
the new registration form is blocked, default is ``False``.

Links
*****

* Download his `PyPi package <http://pypi.python.org/pypi/sveeaccounts>`_;
* Clone it on his `Github repository <https://github.com/sveetch/sveeaccounts>`_;
* Documentation and demo to come on his 
  `DjangoSveetchies page <http://sveetchies.sveetch.net/sveeaccounts/>`_.

Requires
========

* `autobreadcrumbs`_;
* My `django-braces`_ fork;
* `django-registration`_ >= 0.8;
* `django-simple-captcha`_ >= 0.3.4;
* `django-crispy-forms`_ >= 1.1.x;

Install
=======

PIL issue
*********

If you are installing this module within a **virtualenv**, you would have issue with PIL that probably won't be compiled with the **Freetype** support that is used by `django-simple-captcha`_.

To resolve this, uninstall your PIL install within your **virtualenv** : ::

    pip uninstall PIL

Then you will have to install Freetype2 devel library on your system with your prefered package manager, then install `Pillow`_ : ::

    pip install Pillow

It will detect the devel libraries from your system and will compile with their support, problem resolved.

Settings
********

In your *settings* file add the app to your installed apps :

::

    INSTALLED_APPS = (
        ...
        'sveeaccounts',
        ...
    )

Then you have to mount its urls map in your webapp urls.
