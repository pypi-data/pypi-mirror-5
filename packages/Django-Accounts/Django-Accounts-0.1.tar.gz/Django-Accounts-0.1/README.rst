Django-Accounts
===============

Overview
--------
Django-Accounts adds a number of indispensible account-related capabilities to your Django application, including:

* User signup

* Password reset

* Login and logout

* Profile pages

Django-Accounts makes use of class-based views (introduced in Django 1.3) and supports custom user models (introduced in Django 1.5).

Quick Start
-----------
Django-Accounts was designed with a batteries-included philosophy, so it contains everything (including a full set of templates!) that you need to get up and running right away. 

To install Django-Accounts from PyPI::

	pip install django-accounts

Alternatively, you can also install Django-Accounts from GitHub::

	pip install https://github.com/binarybirchtree/django-accounts/archive/master.zip

Add 'accounts' to your INSTALLED_APPS in your settings.py::

	INSTALLED_APPS = (
		...
		'accounts',
		...
	)

Include the Django-Accounts URLs in your urls.py::

	urlpatterns = patterns(
		...
		(r'^accounts/', include('accounts.urls')),
		...
	)

That's it!

License
-------
Django-Accounts is licensed under the GNU General Public License, version 3.

Author
------
Binary Birch Tree

http://www.binarybirchtree.com
