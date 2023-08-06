About Zinnia Drupal
===================

Zinnia Drupal is a small helper application for Django Blog Zinnia that provides
a custom management command that can be used for importing content from Drupal
into Zinnia.


Why was this application created?
---------------------------------

This application was created as the means of migrating my current blog away from
Drupal 6 into Django Blog Zinnia.


Features
--------

Zinnia Drupal has the following features:

* Supports import from Drupal 6 database.
* Imports Drupal users.
  * All users or only a subset.
  * Change username during import.
* Imports Drupal vocabularies, converting them into Zinnia categories.
  * Support for both regular and tag-based vocabularies.
  * Hierarchy is preserved.
  * Vocabulary itself becomes a top-level category.
* Imports Drupal content as Zinnia blog entries.
* Imports Drupal comments.
  * Threaded comments supported (requires zinnia-thraded-comments).
* Import will skip existing data (re-runs should be safe).

There is a couple of limitations in the way the import is performed. Make sure
that you are well aware of those limitations before starting the migration from
Drupal:

* Only the MySQL database is supported at the moment. Despire this, it should be
  easy to extend the code other database since SQLAlchemy is used for accessing
  the Drupal database.
* Non-tag Drupal vocabularies must contain terms that have unique
  names. The import code will not distinguish between same-named terms coming
  from different vocabularies.
* Only username, password, and e-mail is imported for users. I.e. no other
  custom information from users will be imported.
* Users will not be granted any permissions in Zinnia beyond being marked as
  staff. I.e. the users won't be able to create new entries in Zinnia before
  being granted appropriate privileges.
* No formatting conversion is performed. Content is imported as-is.
* Revision history is not preserved (Django Blog Zinnia does not support
  revision history). Only the latest/current revision will be imported.
* Comment *titles* are not part of the import (Django Blog Zinnia does not
  support comment titles).

