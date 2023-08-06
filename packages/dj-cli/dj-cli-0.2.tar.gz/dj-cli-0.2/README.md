
dj
==

**dj** is a command line tool that makes [Django][1] development *even* simpler. It provides shortcuts for most common [manage.py][2] commands.

It uses [virtualenv][3] and [South][4] by default.

Creating New Project
--------------------

    $ dj new myproject/
    New python executable in myproject/bin/python
    Installing Setuptools...
    ...
    
    $ cd myproject/
    
    $ ls -l
    total 0
    drwxr-xr-x  14 user  wheel  476 Nov 15 15:48 bin
    drwxr-xr-x   3 user  wheel  102 Nov 15 15:47 include
    drwxr-xr-x   3 user  wheel  102 Nov 15 15:47 lib
    drwxr-xr-x   6 user  wheel  204 Nov 15 15:50 myproject

Adding New Applications
-----------------------

    $ dj app example
    Creating migrations directory at '/../myproject/example/migrations'...
    Creating __init__.py in '/../myproject/example/migrations'...
    Created 0001_initial.py. You can now apply this migration with: ./manage.py migrate example
    Running migrations for example:
     - Migrating forwards to 0001_initial.
     > example:0001_initial
     - Loading initial data for example.
    Installed 0 object(s) from 0 fixture(s)

This will also update *settings.py* file.

Schema Migration After Model Update
-----------------------------------

    $ vim myproject/example/models.py
    
    $ dj sync example
     + Added model example.Person
    Created 0002_auto__add_person.py. You can now apply this migration with: ./manage.py migrate example
    Running migrations for example:
     - Migrating forwards to 0002_auto__add_person.
     > example:0002_auto__add_person
     - Loading initial data for example.
    Installed 0 object(s) from 0 fixture(s)
    
Shell & Test Server
-------------------

    $ dj shell
    
    $ dj run
    Validating models...
    
    0 errors found
    November 15, 2013 - 14:10:00
    Django version 1.6, using settings 'myproject.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

Installing Packages Inside Virtual Environment
----------------------------------------------

    $ dj install Celery
    Downloading/unpacking Celery
    ...
    
    
Issues / To Do
--------------

* Using bash scripts inside Python, will fix that.
* Argument parser needs to be replaced.
* Deleting applications should be handled manually.

Reporting Bugs, Submiting Pull/Feature Requests
-----------------------------------------------

Feel free to report any bugs, submit pull requests and ask for feature requests.

  [1]: https://www.djangoproject.com/
  [2]: https://docs.djangoproject.com/en/dev/ref/django-admin/
  [3]: http://virtualenv.org
  [4]: http://south.aeracode.org