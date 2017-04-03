.. image:: https://travis-ci.org/ababic/waddleadmin.svg?branch=master
    :alt: Build status
    :target: https://travis-ci.org/ababic/waddleadmin

.. image:: https://img.shields.io/pypi/v/waddleadmin.svg
    :alt: PyPi Version
    :target: https://pypi.python.org/pypi/waddleadmin


What is waddleadmin?
-----------------

It's a playground for me to try out development ideas for `Wagtail <http://docs.wagtail.io/en/latest/>`'s ``contrib.modeladmin`` app.

It's won't ever work reliable, and doesn't have any tests, but it's designed to be compatible with Wagtail 1.9+, and Python 2.7, 3.3, 3.4 and 3.5.

Installing waddleadmin
----------------------

1. Install the package using pip: ``pip install waddleadmin``.
2. Add `wagtail.contrib.modeladmin` to ``INSTALLED_APPS` in your project settings, if it's not there already.
3. Add `waddleadmin` to `INSTALLED_APPS` in your project settings.


Using waddleadmin
-----------------

Simply follow the Wagtail docs for `defining and registering a your model with modeladmin <http://docs.wagtail.io/en/latest/reference/contrib/modeladmin/index.html#how-to-use>`, but instead of doing `from wagtail.contrib.modeladmin.options import ModelAdmin`, do `from waddleadmin.options import ModelAdmin`]


Developing locally
------------------

If you'd like a runnable Django project to help with development of waddleadmin, follow these steps to get started (Mac only). The development
environment has django-debug-toolbar and some other helpful packages installed to help you debug with your code as you develop:

1. In a Terminal window, cd to the `waddleadmin` root directory, and run:  
   `pip install -r requirements/development.txt`
2. Now create a copy of the development settings:  
   `cp waddleadmin/settings/development.py.example waddleadmin/settings/development.py`
3. Now create a copy of the development urls:  
   `cp waddleadmin/development/urls.py.example waddleadmin/development/urls.py`
4. Now create `manage.py` by copying the example provided:  
   `cp manage.py.example manage.py`
5. Now run the following and follow the prompts to set up a new superuser:  
   `python manage.py createsuperuser`
6. Now run the project using the standard Django command:  
   `python manage.py runserver`

Your local copies of `settings/development.py` and `manage.py` should be
ignored by git when you push any changes, as will anything you add to the
`waddleadmin/development/` directory.

