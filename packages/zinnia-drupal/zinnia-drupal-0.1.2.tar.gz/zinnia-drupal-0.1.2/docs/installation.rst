Installation
============

Zinnia Drupal can be installed through one of the following methods:

* Using *pip*, which is the easiest and recommended way for production websites.

Requirements
------------

In order to use Zinnia Drupal it's necessary to install and configure Django
Blog Zinnia itself. There's no special requirements for the import application,
and standard Zinnia documentation should be followed.

Import of threaded comments is possible as well (preserving the hierarchy), but
this requires `Zinnia Threaded Comments
<https://github.com/Fantomas42/zinnia-threaded-comments/>`_. Otherwise the
comments will be imported, but without information about threads.

Using pip
---------

In order to install latest stable release of Zinnia Drupal using *pip*, run the
following command::

  pip install zinnia_drupal

In order to install the latest development version of Zinnia Drupal from Github,
use the following command::

  pip install -e git+https://github.com/azaghal/zinnia-drupal#egg=zinnia_drupal

.. warning::

   You will need to update the ``pip`` installation in your virtual environment if you get the following error while running the above command::

     AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex'

   You can update ``pip`` to latest version with::

     pip install -U pip

After this you should proceed to :ref:`configure your Django installation <configuring-django>`.

.. _configuring-django:

Configuring your Django installation
====================================

Once Zinnia Drupal has been installed, you need to perform the following steps
in order to make it available inside of your Django Blog Zinnia project:

#. Edit your project's settings configuration file (``settings.py``), and update
   the ``INSTALLED_APPS`` to include application ``zinnia_drupal``. Order does
   not matter.

After this you will have :ref:`additional management commands available <usage>`
in your Django Blog Zinnia project that can be used for importing data from
Drupal.

