.. _usage:

Usage
=====

Zinnia Drupal provides custom management commands for importing blogs from
Drupal database. The commands are:

* ``drupal62zinnia``, for importing users, categories, content, and comments
  from Drupal 6 MySQL database.

``drupal62zinnia``
------------------

The command can be called via::

  python manage.py drupal62zinnia [OPTIONS] database_name

The ``database_name`` should be the name of the Drupal database. By default this
database is assumed to be hosted by a MySQL server on the same host where the
command is run.

The following options are available (in addition to standard ones):

``--database-hostname|-H DATABASE_HOSTNAME``
  Hostname of database server providing the Drupal database. Default is
  ``localhost``.

``--database-port|-p DATABASE_PORT``
  TCP port at which the database server is listening. Default is ``3306``.

``--database-username|-u DATABASE_USERNAME``
  Username that should be used for connecting to database server. Default is
  ``root``.

``--database-password|-P DATABASE_PASSWORD_FILE``
  Path to file containing the password for specified database username. If not
  set (default), the password will be read interactively.

``--node-type|-n NODE_TYPE``
  Drupal Node type that should be processed. Default is ``blog``.

``--user-mapping|-m USER_MAPPING``
  Mapping of Drupal usernames to Zinnia usernames. Format is
  ``duser1=zuser1:duser2=zuser2:...:dusern=zusern``. Default is to use same
  username as in Drupal.

``--users|-U USERS``
  Comma-separated list of Drupal users that should be imported, including
  user-created content. Default is to import content from all users.

``--threaded-comments|-t``
  Import comments while preserving threading information. Requires
  zinnia-threaded-comments application. Default is not to use threaded comments.

Examples
--------

Import all blog entries for user ``john``::

  python manage.py drupal62zinnia -u dbuser -U john drupaldb

Import all blog entries for user ``John Doe``, but map the user to user ``john``
in Zinnia::

  python manage.py drupal62zinnia -u dbuser -U john -m 'John Doe=john' drupaldb

Import all blog entries for all users, but map user ``John Doe`` to user
``john`` in Zinnia::

  python manage.py drupal62zinnia -u dbuser -m 'John Doe=john' drupaldb

Import all static pages for all users (treat them as blog entries), connecting
to external database server listening on non-default port, and also use threaded
comments::

  python manage.py drupal62zinnia -H db.example.com -p 3307 -u dbuser -n page -t drupaldb

