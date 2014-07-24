Install the Host Operating System (Fedora 19)
=============================================

For all Linux distributions, you'll need to make sure that the VM will have access to either its own network adapter, for bridged networking, or to a virtual network that is accessible by computers external to the host.
Also, it's best to use the "virtio" network adapter, if the host supports it.

Our deployment server is Fedora 19 (RHEL 7) virtual machine with lots of memory and some CPU space.
When asked to install additional (server) packages, I didn't select any, because we'd probably have installed more software than needed, which is an unnecessary maintenance burden.

Minor Customization and Install Updates
---------------------------------------

Some things that I like to do, but that are entirely optional:

I added "NOPASSWD" to the relevant place in ``/etc/sudoers``, because
there's a lot of ``sudo`` and I don't like putting in my password all
the time.

I updated then restarted system. ::

    $ sudo yum update
    $ sudo systemctl reboot

Configure the Firewall
----------------------

The firewall is enabled by default. We require ports 22, 80, and 443 to be open.

.. note::
        Refer to the "Firewall" chapter of Red Hat's Security Guide for more information: `<https://access.redhat.com/site/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Security_Guide/sec-Using_Firewalls.html>`__.

Run the following commands to configure the firewall:::

    sudo firewall-cmd --permanent --add-service http
    sudo firewall-cmd --permanent --add-service https
    sudo firewall-cmd --permanent --add-service ssh

Ensure SELinux is active. The default configuration is sufficient for now::

    sudo getenforce

If SELinux is not running, activate it with::

    sudo setenforce 1

Add tmpfs for Runtime Files
---------------------------

NOTE THAT I DIDN'T DO THIS FOR THE DATABASE SERVER

I added an in-memory temporary directory for the Web app's temporary
files. This will give us mildly improved speed and security. The
directory will not mount properly until after you install the Web app.
Change the value of the "size" mount option according to how much memory
your server has. In ``/etc/fstab``, add:

::

    tmpfs   /usr/local/vis_counterpoint/runtime/outputs     tmpfs   size=8G,nodev,noexec,nosuid,uid=www-data,gid=www-data,mode=770     0 0

Configure the Network
---------------------

I don't remember how I did this, but it wasn't obvious at first because I'd never used NetworkManager from the commandline before.

Install the Database App and Its Dependencies
=============================================

Install Git
-----------
::
    $ sudo yum install git

Setup Directories
-----------------
::
    $ cd /usr/local
    $ sudo mkdir elvis_database

Install Solr
------------

Clone the Solr template for Maven::
    $ sudo git clone https://github.com/DDMAL/solr-mvn-template

Install Tomcat and Maven::
    $ sudo yum install tomcat maven

Edit the ``pom.xml`` file so it's like this::
        <groupId>ca.elvisproject.database</groupId>
        <artifactId>elvis-solr</artifactId>
        <name>Solr Instance for the ELVIS Database</name>
        <url>http://database.elvisproject.ca/</url>
        ...
        <build>
            <finalName>elvis-solr</finalName>

In ``solr/collection1/conf/solrconfig.xml``::
    <dataDir>/var/db/solr/elvis-solr</dataDir>

--> CRA: may need SELinux and permissions adjustment for the "tomcat" user

In the ``solr/collection1/conf/schema.xml``::
    <schema name="elvis-solr" version="1.5">

IMPORTANT Modify $CATALINA_HOME/conf/Catalina/localhost/solr.xml. See readme in solr-mvn-template:
    " ) Configure a Context fragment

        cp tomcat-context.xml $CATALINA_HOME/conf/Catalina/localhost/solr.xml

    and edit the `solr/home` `<Environment>` value. Note that you can set up
    as many different contexts as you want with different `solr/home` values,
    each using the same `solr.war`"


Make sure you're in the same directory as ``pom.xml``, then run::
    $ sudo mvn package

Install the Solr app by copying it to the Tomcat apps directory::
    $ sudo cp target/elvis-solr.war /var/lib/tomcat/webapps

And change its ownership::
    $ sudo chown :tomcat /var/lib/tomcat/webapps/elvis-solr.war

Make the Solr database directory and set its permissions::
    $ sudo mkdir /var/db/solr
    $ sudo chown tomcat:tomcat /var/db/solr

Enable and start the Tomcat service::
    $ sudo systemctl enable tomcat
    $ sudo systemctl start tomcat

Temporarily modify the firewall rules to allow viewing the Tomcat server on port 8080. This rule is automatically reverted after 5 minutes (300 seconds)::
    $ sudo firewall-cmd --add-port=8080/tcp --timeout=300

Check that Solr works by visiting ``<hostname>:8080/elvis-solr/`` in a Web browser.
We will configure Solr for the ELVIS Database later.

Set SELinux to allow the Apache httpd Server to connect to Solr:::
    $ sudo setsebool -P httpd_can_network_connect 1

Install RabbitMQ
----------------

Install the server:::
    $ sudo yum install rabbitmq-server

Enable:::
    $ sudo systemctl enable rabbitmq-server
    $ sudo systemctl start rabbitmq-server



Install PostgreSQL
------------------

I don't know. I'll do this in a minute.

::
    $ sudo yum install postgresql postgresql-server

Initialize the database::
    $ sudo postgresql-setup initdb

Enable PostgreSQL and start the server::
    $ sudo systemctl enable postgresql
    $ sudo systemctl start postgresql

Create the Database's database user. Use a good password for the database user.::
    $ sudo passwd postgres
    <something easy>
    $ su postgres
    $ psql
    # CREATE USER elvisdatabase PASSWORD '';
    CREATE ROLE
    # CREATE DATABASE elvisdatabase OWNER elvisdatabase;
    CREATE DATABASE
    # \q

--> TODO: change the "postgres" user password, or else you won't be able to log in with it after the next step

Change the "postgres" user's password to something difficult to guess.::
    $ exit
    $ sudo passwd postgres
    <something difficult>

Finally, update this line in ``/var/lib/pgsql/data/pg_hba.conf``::
    local   all             all                                     peer

    ... to...

    local   all             all                                     password

Restart the PostgreSQL server::
    $ sudo systemctl restart postgresql

Install the Web Server
----------------------

We recommend you use the Apache HTTPD Web server, because we do.
Refer to the "Web Servers" chapter of the Red Hat System Administrators' Guide at `https://access.redhat.com/site/documentation/en-US/Red_Hat_Enterprise_Linux/7-Beta/html/System_Administrators_Guide/ch-Web_Servers.html`__ for more information.

.. note::

    If required, you must configure port forwarding and other router and hypervisor network settings before this step.

Install the Apache HTTP Server::
    $ sudo yum install httpd mod_wsgi

Edit the host files to remove unnecessary bits.

    #. Delete ``/etc/httpd/conf.d/manual.conf``. This is the HTTP Server manual.
    #. Delete ``/etc/httpd/conf.d/autoindex.conf``. This would provide automated directory listings and icons by MIME-type.
    #. Delete ``/etc/httpd/conf.d/userdir.conf``. This would serve content from ``public_html`` in user directories.
    #. Delete ``/etc/httpd/conf.d/welcome.conf``. This would serve a default "welcome" page while the server is not configured.

Edit the server's general configuration file at ``/etc/httpd/conf/httpd.conf``::
    ServerName cwa-devel.elvisproject.ca  # (modified as required)
    ServerSignature Off
    ServerTokens Prod

Install the ELVIS Database Django Application
---------------------------------------------

Complete the following procedure to install the ELVIS Database Django Application (EDDA) using the virtualenv package.
We recommend you use a "virtualenv" environment, but you may use system packages with little modification.

    #. Clone the EDDA's Git repository::
        $ sudo git clone git://github.com/ELVIS-Project/elvis-site.git

    #. Install "virtualenv" and other required software::
        $ sudo yum install python-virtualenv python-devel gcc-c++ postgresql-devel

    #. Initialize then activate the EDDA's virtualenv environment::
        $ sudo virtualenv /usr/local/elvis_database/edda_virtualenv
        $ sudo -i
        $ cd /usr/local/elvis_database
        $ source edda_virtualenv/bin/activate

        .. note::
            Because virtualenv works by modifying environment variables, you must run all virtualenv-related commands in an interactive shell.
            If you ``source`` the virtual environment as a regular user, then use pip with ``sudo``, pip will install all packages to the system ``site-packages`` directory.

    #. Update pip::
        $ pip install -U pip

    #. Use pip to install the EDDA's dependencies::
        $ pip install -r elvis_site/requirements.txt

       Note that, if mysql isn't installed, then it is required for MySQL-Python and the package for mysql should be installed through yum

    #. If pip cannot find a satisfactory Django version, find the URL manually from the `Django website<hthttps://www.djangoproject.com/download/>`__ then re-run the previous command. ::
        $ pip install https://www.djangoproject.com/download/1.7.b4/tarball/

Configure the ELVIS Database Django Application
===============================================

Reconfigure Solr
----------------

We must configure Solr for use with the ELVIS Database Django Application (EDDA).

    #. Copy the Solr schema from the EDDA repository to the Solr build directory::
        $ sudo cp /usr/local/elvis_database/elvis-site/solr/src/main/resources/schema.xml /usr/local/elvis_database/solr-mvn-template/solr/collection1/conf

    #. Rebuild and reinstall the Solr instance. Run the following commands (copied from above)::
        $ sudo mvn package
        $ sudo cp target/elvis-solr.war /var/lib/tomcat/webapps
        $ sudo chown :tomcat /var/lib/tomcat/webapps/elvis-solr.war

    #. Restart the Solr server and check its operation::
        $ sudo systemctl restart tomcat
        $ sudo firewall-cmd --add-port=8080/tcp --timeout=300
        (Visit <hostname>:8080/elvis-solr in a Web browser)

Configure the Database with the EDDA
------------------------------------
First, edit ``settings.py``::
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'elvisdatabase',
            'USER': 'elvisdatabase',
            'PASSWORD': '',  # set this as requried
            'HOST': '',  # "localhost through domain sockets"
            'PORT': '',  # "default" (5432)
        }
    }

Be sure you're in the virtualenv, then syncdb::
    $ activate /usr/local/elvis_database/edda_virtualenv/bin/activate
    $ python /usr/local/elvis_database/elvis-site/elvis/manage.py syncdb

Media and Static File Folders for the EDDA
------------------------------------------
::
    $ sudo mkdir /usr/local/elvis_database/media_root
    $ sudo chown apache:apache /usr/local/elvis_database/media_root
    $ sudo semanage fcontext -a -t httpd_sys_rw_content_t /usr/elvis_database/media_root
    $ sudo restorecon -v /usr/local/elvis_database/media_root

    $ sudo mkdir /usr/local/elvis_database/static_root
    $ sudo chown apache:apache /usr/local/elvis_database/static_root
    $ sudo semanage fcontext -a -t httpd_sys_content_t /usr/elvis_database/static_root
    $ sudo restorecon -v /usr/local/elvis_database/static_root

.. note:: The ``semanage`` commands above *are* /usr/elvis_database, *not* /usr/local/elvis_database.

And collect static files:::
    $ python manage.py collectstatic

Configure the Apache HTTP Server
--------------------------------

In one of the files in /etc/httpd/conf.d, adjust the following things:

    * WSGIScriptAlias first\_thing second\_thing.
        * The first\_thing is the URL path; use ``/`` for the root. This must not end with a trailing slash.
        * The second\_thing is the path to the django\_vis directory. It must be the full pathname, not the python module.
    * Make sure the <Directory> directive has the directory of the wsgi.py file.
    * Add Alias directives for static files.

You get something like this:::
    <VirtualHost *:80>
        ServerName db-devel.elvisproject.ca
        ServerAdmin webmaster@elvisproject.ca
        WSGIScriptAlias / /usr/local/elvis_database/elvis-site/elvis/elvis/wsgi.py
        WSGIDaemonProcess db.elvisproject.ca processes=2 threads=15 display-name=%{GROUP}
        WSGIProcessGroup db.elvisproject.ca

        # for wsgi.py
        <Directory /usr/local/elvis_database/elvis-site/elvis/elvis>
            # for Apache 2.2
            # Order allow,deny
            # Allow from all
            # for Apache 2.4
            Require all granted
        </Directory>

        # for static_root
        <Directory /usr/local/elvis_database/static_root>
            # for Apache 2.2
            # Order allow,deny
            # Allow from all
            # for Apache 2.4
            Require all granted
        </Directory>

        # for media_root
        <Directory /usr/local/elvis_database/media_root>
            # for Apache 2.2
            # Order allow,deny
            # Allow from all
            # for Apache 2.4
            Require all granted
        </Directory>

        DocumentRoot /var/www

        # TODO: fix these Alias directives
        #Alias /robots.txt /usr/local/vis_counterpoint/web-vis/robots.txt
        #Alias /humans.txt /usr/local/vis_counterpoint/web-vis/humans.txt
        #Alias /favicon.ico /usr/local/vis_counterpoint/web-vis/favicon.ico
        Alias /static /usr/local/elvis_database/static_root

        ErrorLog /var/log/httpd/elvisdb_error.log
        CustomLog /var/log/httpd/elvisdb_access.log common
    </VirtualHost>

Restart httpd: ``$ sudo systemctl restart httpd``


Populate Database 
-----------------
Prepare sql dump files, and elvis attachment files

Install mariaDB, and import the dump files to their respective databases

Run dump_drupal.py as root (sudo -i, activate environment, then python dump_drupal.py)




Other Settings
--------------

For final deployment, adjust the following settings.

In ``settings.py``, FOR NOW there's only this:::

    PRODUCTION = True
    SECRET_KEY = ''  # (you have to put 50 pseudo-random characters here)

Uncomment the following lines in ``wsgi.py``:::

    import imp
    try:
        imp.find_module('elvis')
    except ImportError:
        import sys
        sys.path.append('/usr/local/elvis_database/elvis-site/elvis/')

In addition, if you installed the EDDA with virtualenv, uncomment the following lines in ``wsgi.py``:::

    activate_this = '/usr/local/elvis_database/edda_virtualenv/bin/activate_this.py'
    execfile(activate_this, dict(__file__=activate_this))


------> TODO FIRST!!!!!!!!!!!!!!!: figure out SECRET_KEY
------> TODO: add a thing about Celery and RabbitMQ or whatever



Celery Service for Downloads using Supervisord
--------------------––––––––------------------

Install supervisord package
    sudo yum install supervisord

Make celery_start.sh script in elvis_database to
    1. start virtual environment
    2. run celery worker in that virtual environment
    3. run celery beat in that virtual environment
    
    It should look something like this (replace execution with celery -A elvis beat --pidfile="/run/celery/%n.pid --schedule=/var/lib/celery/celerybeat-schedule... for the cron):

    #!/bin/bash

    # Virtual env path
    VIRTUAL_ENV=/usr/local/elvis_database/edda_virtualenv
    PROJECT_PATH=/usr/local/elvis_database/elvis-site/elvis
    # Activate
    source ${VIRTUAL_ENV}/bin/activate
    # Move to project directory
    cd ${PROJECT_PATH}
    # Run your worker... old: exec celery worker -A elvis -l DEBUG --loglevel=INFO 
    exec celery worker -A elvis --pidfile="/run/celery/%n.pid"


Make a user: celery with usergroup celery. It should have /sbin/nologin for its shell

Edit /etc/supervisord.conf to include a celery 'programme' to supervise. It should have the following things (replace accordingly for celery_beat_start.sh):
    [program:elvis-celery]
    command=/usr/local/elvis_database/elvis-site/elvis/celery_start.sh
    directory=/usr/local/elvis_database/elvis-site/elvis
    chown=celery:celery
    user=celery
    autostart=true
    autorestart=true
    redirect_stderr=true
    redirect_stdout=true
    stdout_logfile = /var/log/celery/supervised_celery.log
    stderr_logfile = /var/log/celery/supervised_celery.log
    stdout_logfile_maxbytes=50MB
    killasgroup=true


Make sure that the prority for rabbitmq is higher than supervisord on startup

Celery will attempt to write into MEDIA_ROOT/user_downloads. If that directory doesn't exist, celery would probably not be able to write into MEDIA_ROOT. This is because MEDIA_ROOT is owned by Django. So, mkdir /user_downloads and chown celery:celery.





TODO: Consider These Settings
-----------------------------
- EMAIL_BACKEND and related
- CSRF_COOKIE_SECURE and SESSION_COOKIE_SECURE
- CONN_MAX_AGE and TEMPLATE_LOADERS
- ADMINS and MANAGERS
- Check supervisord: searches for supervisord.conf & security concerns over fake .conf file


Other Things
------------
TODO-NOTE: this section is from the CWA Deployment Guide, and probably needs to be changed...

Set the timezone.

Make sure ``/tmp/music21`` is owned by www-data:www-data with read/write
744 permissions.

TODO: figure out how to change the "scratch files" directory without
using the ``~/.music21rc`` file.

Make the VIS temp directories:

``$ sudo mkdir /usr/local/vis_counterpoint``

``$ sudo mkdir /usr/local/vis_counterpoint/outputs``

``$ sudo chown -R www-data:www-data /usr/local/vis_counterpoint``

Use this terribly hacky way to create the sqlite3 database file:

``$ sudo passwd www-data`` (to something easy)

``$ su www-data``

``$ python manage.py syncdb`` (choose "no" when asked about
"superusers")

``$ exit``

``$ sudo service apache2 restart``

``$ sudo passwd www-data`` (to something incredibly difficult)
