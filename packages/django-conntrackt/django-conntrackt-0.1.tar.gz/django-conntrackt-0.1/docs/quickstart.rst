.. Copyright (C) 2013 Branko Majic

   This file is part of Django Conntrackt documentation.

   This work is licensed under the Creative Commons Attribution-ShareAlike 3.0
   Unported License. To view a copy of this license, visit
   http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to Creative
   Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.


Quick-start guide
=================

This chapter provides quick-start instructions in order to allow you to quickly deploy and test Django Conntrackt application.


Debian/Ubuntu
-------------

Install the *pip* utility::

  sudo apt-get install pip

Install the *virtualenv* and *virtualenvwrapper*::

  sudo apt-get install python-virtualenv virtualenvwrapper

Create the virtual environment for testing Django Conntrackt::

  mkvirtualenv conntrackt

Install Django Conntrackt with its requirements::

  workon conntrackt
  pip install -e hg+http://code.majic.rs/conntrackt#egg=conntrackt

.. warning::

   You will need to update the ``pip`` installation in your virtual environment if you get the following error while running the above command::

     AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex'

   You can update ``pip`` to latest version with::

     pip install -U pip

Start a new Django Conntrackt project::

  django-admin.py startproject conntrackt_test

Edit configuration file ``conntrackt_test/conntrackt_test/settings.py`` to set-up
some basic settings:

#. Under ``DATABASES`` set parameter ``ENGINE`` to ``'django.db.backends.sqlite3'``.
#. Under ``DATABASES`` set parameter ``NAME`` to ``'conntrackt_test.sqlite'``.
#. Under ``INSTALLED_APPS`` uncomment the line ``'django.contrib.admin'``.
#. Under ``INSTALLED_APPS`` append lines::

     'south',
     'braces',
     'conntrackt',

#. Append the following lines to the end of the file::

     from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
     TEMPLATE_CONTEXT_PROCESSORS += (
         "django.core.context_processors.request",
     )


Edit the URL configuration file ``conntrackt_test/conntrackt_test/urls/.py`` to
set-up the URLs for the admin website and Conntrackt itself:

#. At the top of the file, add line ``from django.http import HttpResponseRedirect``.
#. Uncomment line ``from django.contrib import admin``.
#. Uncomment line ``admin.autodiscover()``.
#. Uncomment line ``url(r'^admin/', include(admin.site.urls)),``
#. Under ``urlpatterns`` append lines::

     url(r'^$', lambda r : HttpResponseRedirect('conntrackt/')),
     url(r'^conntrackt/', include('conntrackt.urls')),

Set-up the database for the project::

  python manage.py syncdb

You will be prompted to provide some additional information:

#. When prompted to create a superuser, answer ``yes``.
#. Provide the desired username when prompted for it.
#. Provide the desired e-mail address when prompted for it.
#. Provide the desired password for created user.

After this the project is fully configured to run Django Conntrackt. Run the
Django development server (good enough for testing, but don't use it in
production)::

  python manage.py runserver

You can now explore the functionality of Djang Conntrackt at::
  http://localhost:8000/

If you have any problems getting around and understanding how the applications
works, have a look at the :ref:`usage guide <usage>`.

