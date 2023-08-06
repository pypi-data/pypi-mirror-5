
django-mobilvest
===============
https://bitbucket.org/ir4y/django-mobilvest

What's that
-----------

*django-mobilvest is a application for sending sms over mobilvest.ru web gate

Dependence
-----------

- `django-celery` # for sending async request
- `pycurl` # for http communication

Getting started
---------------
* Install django-mobilvest:

``pip install -e https://bitbucket.org/ir4y/django-mobilvest#egg=django-mobilvest
``

* Add `'mobilvest'` to INSTALLED_APPS.

* Add MOBILVEST_USER and MOBILVEST_PASSWORD to your settings file