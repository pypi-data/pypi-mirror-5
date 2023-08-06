.. Copyright (C) 2013 Branko Majic

   This file is part of Django Conntrackt documentation.

   This work is licensed under the Creative Commons Attribution-ShareAlike 3.0
   Unported License. To view a copy of this license, visit
   http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to Creative
   Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.


Installation
============

Django Conntrackt can be installed through one of the following methods:

* Using *pip*, which is the recommended way for production
  websites.


Using pip
---------

In order to install latest stable release of Django Conntrackt using *pip*, use
the following command::

  pip install conntrackt

In order to install the latest development version of Django Conntrackt from
Mercurial repository, use the following command::

 pip install -e hg+http://code.majic.rs/conntrackt#egg=conntrackt

.. warning::

   You will need to update the ``pip`` installation in your virtual environment if you get the following error while running the above command::

     AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex'

   You can update ``pip`` to latest version with::

     pip install -U pip

After this you should proceed to :ref:`configure your Django installation <configuring-django>`.


.. _configuring-django:

Configuring your Django installation
====================================

Once the Django Conntrackt has been installed, you need to perform the following
steps in order to make it available inside of your Django project:

#. Edit your project's settings configuration file (``settings.py``), and update
   the ``INSTALLED_APPS`` to include applications ``south``, ``braces`` and ``conntrackt``.

#. Edit your project's URL configuration file (``urls.py``), and add the
   following line to the ``urlpatterns`` setting::

     url(r'^conntrackt/', include('conntrackt.urls')),

#. Create the necessary tables used for Django Conntrackt by running::

   ./manage.py syncdb

After this the Django Conntrackt application will be available under the
``/conntrackt/`` path (relative to your Django project's base URL).

If you have enabled ``django.contrib.admin``, you should be able to add new
Conntrackt data through the admin interface.
