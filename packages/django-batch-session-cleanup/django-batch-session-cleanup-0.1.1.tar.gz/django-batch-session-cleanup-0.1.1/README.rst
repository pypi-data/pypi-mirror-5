Django Session Space Analysis Tool
==================================

This is a Django management command (as in
https://docs.djangoproject.com/en/dev/howto/custom-management-commands/)
that cleans up expired sessions from the database.

Why?
----

Django ships with a built-in command to handle session cleanup, but it
is problematic when dealing with large session tables. Due to its
design, it can block writes to the session table for minutes at a time,
potentially disrupting sites that rely on sessions. This command is
designed to perform the same maintenance tasks as the built-in command
without disrupting a site by locking the table for a really long time.

Installation
------------

Install the distribution from PyPI, e.g. ``pip install
django-batch-session-cleanup``.

Then, add ``batch_sesion_cleanup`` to INSTALLED_APPS in your Django project.

That's it. You can now run django-admin.py and confirm that the command
shows up.

Example Uses
------------

Delete expired sessions in batches of no more than 50000, and sleep for
2 seconds in between batches:::

    django-admin.py batch-session-cleanup --batch-size=50000 --sleep-time=2

Known Issues and Bugs
---------------------

- The tool has only been tested thoroughly on a MyISAM MySQL table. I'm not aware of any reason that it wouldn't work on other SQL session backends, but you should be careful if you're using it in those environments.

Author
------

Kevan Carstensen <kevan@isnotajoke.com>
