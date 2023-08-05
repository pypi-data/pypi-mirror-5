.. -*- coding: utf-8 -*-

=======
Upgrade
=======

:Author: Étienne Loks
:date: 2013-03-16
:Copyright: CC-BY 3.0

This document presents the upgrade of Chimère.

.. Warning::
   Before any upgrade backup the database and all your installation files
   (specially if you have made changes to them).

The process for migration requires a basic knowledge of Git and Linux CLI. It is
*not* an easy process. A work is currently done to easy the upgrade in later 
versions (>2.0) of Chimère.

If several versions have been published, you should repeat all upgrading steps.
For instance to upgrade from v1.1 to v2.0 you should first upgrade to v1.2 then
to v2.0. The only optional step is the integration of your customisations.

The current stable version is 2.0.

.. Note::
   If you are considering to contribute on Chimère get the Git master.

The instructions are given for Debian Squeeze and Debian Wheezy.


Getting new versions of dependencies
------------------------------------

If you want to install the Chimère package for Debian Wheezy dependencies are
managed by the package.
You can go to the next section of the documentation.

Version 1.1 -> 1.2
******************

.. code-block:: bash

    apt-get install python-lxml libjs-jquery gpsbabel python-gdal

Version 1.2 -> 2.0
******************

Debian Squeeze
++++++++++++++
Activate the backports: http://backports-master.debian.org/Instructions/
Then install the new dependencies::

    apt-get install -t squeeze-backports python-django python-django-south \
                       python-simplejson libjs-jquery-ui python-pyexiv2 \
                       python-feedparser javascript-common libjs-jquery

Debian Wheezy
+++++++++++++

.. code-block:: bash

    apt-get install python-django-south python-simplejson libjs-jquery-ui \
                    python-pyexiv2 python-feedparser javascript-common

If you are planning to do major import consider the install of `Celery
<http://celeryproject.org/>`_.

.. code-block:: bash

    apt-get install python-django-celery python-kombu

Getting the new sources
-----------------------

To simplify further instructions, some environment variables are
initialized.

.. code-block:: bash

    CHIMERE_PATH=/srv/chimere
    CHIMERE_BRANCH=v1.2        # version 1.1 -> 1.2
    CHIMERE_BRANCH=v2.0        # version 1.2 -> 2.0
    CHIMERE_BRANCH=master      # version 2.0 -> master
    CHIMERE_LOCALNAME=mychimere

Your local name is used for the name of your local Git branch and the Python
package. As a Python package it should follow the rule of Python variable name:
it must be at least one letter and can have a string of numbers, letters and
underscores ("_") to any length. Don't begin the name by "_" because it has special
significance in Python.

From Debian package
*******************

If you want to install the last stable version of Chimère
and your system is under Debian Wheezy it is wise to use
Chimère Debian packages.

If you have a previous installation from sources remove
all chimère libraries but **keep** your project dir.

.. code-block:: bash

    rm -rf $CHIMERE_PATH/chimere

Then you can install Chimère.

.. code-block:: bash

    # add Chimère repository
    echo "deb http://debian.peacefrogs.net wheezy main" >> /etc/apt/sources.list
    apt-get update
    # install
    apt-get install python-django-chimere


Installation from sources
*************************

First of all you have to get the new version of the source code.
For the upgrade process, the source code has to be from the Git
repository.

From a previous Git installation
++++++++++++++++++++++++++++++++

.. code-block:: bash

    cd $CHIMERE_PATH
    git stash # if you have uncommited changes
    git checkout origin/$CHIMERE_BRANCH -b $CHIMERE_LOCALNAME

From a previous tarball installation
++++++++++++++++++++++++++++++++++++

First remove your old installation and get the Git version:

.. code-block:: bash

    cd $CHIMERE_PATH
    cd ..
    rm -rf $CHIMERE_PATH
    git clone git://www.peacefrogs.net/git/chimere
    cd chimere
    git checkout origin/$CHIMERE_BRANCH -b $CHIMERE_LOCALNAME


Update basic settings
*********************

Version 1.1 -> 1.2
++++++++++++++++++

.. code-block:: bash

    CHIMERE_APP_PATH=$CHIMERE_PATH/chimere
    vim $CHIMERE_APP_PATH/settings.py

Add the following lines (adapted for your jquery and gpsbabel installation):

.. code-block:: python

    JQUERY_URL = SERVER_URL + 'jquery/jquery-1.4.4.min.js'
    GPSBABEL = '/usr/bin/gpsbabel'
    # simplify with an error of 5 meters
    GPSBABEL_OPTIONS = 'simplify,crosstrack,error=0.005k'

Version 1.2 -> 2.0
++++++++++++++++++

Project template
................
A default project can be found on `Gitorious
<https://gitorious.org/chimere-example-project/chimere-example-project>`_. Get
it and start a new project with it (or get another project based on Chimère):

.. code-block:: bash

    cd $CHIMERE_PATH
    git clone git://gitorious.org/chimere-example-project/chimere-example-project.git
    django-admin startproject --template=chimere-example-project mychimere_project
    rm -rf chimere-example-project

local_settings
..............
A *local_settings* file is now used.

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    cp local_settings.py.sample local_settings.py
    vim local_settings.py

Report your old settings from *settings.py* to *local_settings.py* (at least the
database configuration).
The setting *ROOT_URLCONF* must be set to **value_of_your_localname.urls**.

logs
....
Logging is now enabled by default in the file */var/log/django/chimere.log*.

.. code-block:: bash

    mkdir /var/log/django
    touch /var/log/django/chimere.log
    chown www-data -R /var/log/django

Static files
............

Now static files are managed with *django.contrib.staticfiles*.

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    ./manage.py collectstatic

Move old static files to the new static directory:

.. code-block:: bash

    cp -ra $CHIMERE_PATH/chimere/static/* $CHIMERE_APP_PATH/static/
    cp -ra $CHIMERE_PATH/chimere/static/icons/* $CHIMERE_APP_PATH/media/icons/
    cp -ra $CHIMERE_PATH/chimere/static/upload $CHIMERE_APP_PATH/media/
    rm -rf $CHIMERE_PATH/chimere/static/icons
    rm -rf $CHIMERE_PATH/chimere/static/upload

Update permissions for media directory:

.. code-block:: bash

    chown www-data -R $CHIMERE_APP_PATH/media/


Webserver configuration
.......................
If you are using Apache and WSGI to serve your Chimère, change your WSGI
configuration file to point to the correct settings:
**value_of_your_localname.settings**.

Change your webserver directive to point to the correct static directory from
**your_chimere_path/chimere/static** to
**your_chimere_path/your_local_name/static**.

Version 2.0 -> master
+++++++++++++++++++++

Update settings and static files.

.. code-block:: bash

    cp $CHIMERE_PATH/example_project/settings.py $CHIMERE_LOCALNAME
    ./manage.py collectstatic

Migrate database
----------------

Version 1.1 -> 1.2
******************

Migration scripts test your installation before making changes so you probably
won't have any lost but by precaution before running these scripts don't forget
to backup your database.
You can also make a copy of your current database into a new database and make
the new installation to this new database.

The gdal binding for Python is necessary to run the upgrade scripts (available
in the python-gdal package in Debian).

If you run the migration scripts in a production environnement stop the old
instance of Chimère before executing the migration script.

In *settings.py* verify that **chimere.scripts** is in the *INSTALLED_APPS*.

After that in the Chimère directory just execute the script.

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    python ./scripts/upgrade.py

Version 1.2 -> 2.0
******************

Django South is now used to manage database migrations.

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    ./manage.py syncdb --noinput
    ./manage.py migrate chimere 0001 --fake # fake the database initialisation
    ./manage.py migrate chimere

A description field is now available for markers. If you would like to move
values of an old *Property model* to this new field, a script is available.

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    ../chimere/scripts/migrate_properties.py
    # follow the instructions

Version 2.0 -> master
*********************

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    ./manage.py syncdb
    # les migrations ont été réinitialisées
    ./manage.py migrate chimere --delete-ghost-migrations --fake 0001
    ./manage.py migrate chimere

Update translations
-------------------

Version 1.1 -> 1.2
******************

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    ./manage.py compilemessages

Version 1.2 -> 2.0 -> master
****************************

.. code-block:: bash

    cd $CHIMERE_PATH/chimere
    django-admin compilemessages


Forcing the refresh of visitor's web browser cache
--------------------------------------------------

Major changes in the javascript has been done between versions, many of your
users could experience problems. There are many tricks to force the refresh
of their cache. One of them is to change the location of statics files. To do
that edit your local_settings.py and change::

    STATIC_URL = '/static/'

to::

    STATIC_URL = '/static-v2.0.0/'

Then change the webserver directive to point to your new path.
Restart the web server to apply this changes.

Configuring the Sites framework
-------------------------------

Version 1.2 -> 2.0
******************

*Sites* framework allow you to serve the same content on different domains.
Most of you will probably use only one domain but this unique domain has to
be configured. This is done in the web administration interface in *Sites > Sites*.
You only need to change *example.com* by your domain name. If you forget to
do that, some functionalities such as RSS feeds will not work properly.

