# Initialization
We're installing the project on a compute canada virtual machine instance with Ubuntu 16 installed. If installing on a different environment, the only real requirement is that the OS is POSIX compliant and that all the software listed in the 'Required Software' section can run on it. That said, running with Ubuntu will likely vastly simplify installing all the requirements of the project, and you will be able to follow this guide more closely.

I like to set up a user responsible for running the project and having ownership over the project's files and services. This simplifies privileges and makes it easy for multiple users to administrate the project.

If you're running on a freshly installed OS, make sure to download the newest versions of the base software with your package manager.
```
sudo apt update
sudo apt upgrade
```

We will make a new user called `elvisdb` to run the project.

```
sudo useradd --system --shell /bin/bash --home /home/elvisdb elvisdb
```

If your system does not have nice shell defaults for new users, you might be able to grab some from the `ubuntu` user (this may be very particular to Compute Canada).
```
sudo cp -r /home/ubuntu/{.profile,.bashrc} /home/elvisdb
```

Itf you decide to give the `elvisdb` user sudo power to aid with the installation process, you might want to consider revoking it before going into production. Whether or not this makes sense will depend on how you access the server (local or ssh), whether or not you are using public keys (you should), and on which network the machine is deployed. Since the machine on compute canada is deployed on a private network, behind a proxy-machine which only lets through requests on port 80, it should be fairly safe to give the `elvisdb` user sudo power.

# Required Software

Before we start setting up the project in earnest, we need to install all of the following software. It is possible, especially if you are using an OS other than Ubuntu, that some software you will need is missing from this list. In this case, use google and read error messages carefully to figure out which dependency you are missing.

You will need to install the following packages on Ubuntu.

* python3
* python3-dev
* python-software-properties 
* git
* java8
* supervisor
* nginx
* build-essential
* virtualenv
* postgreSQL
* libpq-dev
* libncurses5-dev
* build-essential
* tcl

You can install all of the above on Ubuntu using the following command:
```
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt install python3 python3-dev python-software-properties git virtualenv postgresql-contrib postgresql oracle-java8-installer libpq-dev  libncurses5-dev build-essential supervisor tcl nginx
```

In addition to the above, you will need to install the following services manually. All of the following must be installed and running as daemons in order to support the project.

## rabbitmq
rabbitmq is a message passer used by celery. You can find installation instructions at https://www.rabbitmq.com/install-debian.html

## solr
Solr is a fast search engine which powers the site's search feature. You can find detailed installation instructions at http://lucene.apache.org/solr/.

At the time of writing, installing solr is quite straightforward:

1. Download the latest binary distribution from http://lucene.apache.org/solr/mirrors-solr-latest-redir.html
2. Assuming you downloaded the .tgz file for solr version X.Y.Z into your home directory, follow these steps to install the solr service:
```
tar -xvf ~/solr-X.Y.Z.tgz
sudo ~/solr-X.Y.Z/bin/install_solr_service.sh ~/solr-X.Y.Z.tgz
```
You can verify the above worked by running `curl localhost:8983/solr/`. If everything is working, it will return a lengthy html response. You can also use `sudo systemctl status solr` to check the status of the new daemon.

## supervisor
You should have installed supervisor via the ubuntu package manager in the above section. In order to assure it is running, run `sudo systemctl status supervisor`. If it is not running, you may need to enable the service by running `sudo systemctl enable supervisor`. If these commands read like witchcraft, you may want to learn the [bare minimum about systemd.](https://www.digitalocean.com/community/tutorials/systemd-essentials-working-with-services-units-and-the-journal) 

## redis
redis is an in memory key-value based cache. You can find installation instructions at http://redis.io/

At the time of writing, a nice guide for installing redis is available at https://www.digitalocean.com/community/tutorials/how-to-install-and-use-redis

Once redis is set up, no further configuration is necessary.
    
# Setup
We need to set up the deployment directory.
```
sudo mkdir -p /srv/webapps/elvisdb/{config,media,static}
sudo chown elvisdb:elvisdb /srv/webapps/elvisdb
```

From now on, I will refer to `/srv/webapps/elvisdb` as `$ELVIS_HOME`

*Note: on the active deployment of the production server, a file named /home/elvisdb/elvis-env.sh contains a list of variables and their definitions which may be helpful for navigating the server.*

While in `$ELVIS_HOME`, run the following command:
```
git clone https://github.com/ELVIS-Project/elvis-database.git
```

This will create a directory `$ELVIS_HOME/elvis-database/`. Lets go into this directory and create a python 3 virtual environment, source it, and install the project's python requirements.
```
cd $ELVIS_HOME/elvis-database/
virtualenv --python=python3 .env
source .env/bin/activate
pip install -r requirements.txt
```

Lastly, we need to change one setting in the project configuration file to make it aware that we are doing a production deployment. Open up `$ELVIS_HOME/elvis-database/elvis/settings.py`, and change the`SETTING_TYPE` variable from `LOCAL` to `PRODUCTION` (or to `DEVELOPMENT`, if you're sure that's what you want... read the comments in the file!).

Now the basic environment for the project is set up, we can begin connecting the various components together.

## Connecting postgreSQL
The project expects there to be a postgreSQL database called `elvis_database` owned by a user named `elvisdb` with a password stored in `$ELVIS_HOME/config/db_pass`.

First, lets generate a password and save it in `$ELVIS_HOME/config/db_pass`. You can use any password you like, but a long, random one is best. You should make sure to save this password offsite. One way to generate a password:
```
openssl rand -base64 32 > $ELVIS_HOME/config/db_pass
```

Now is also a good time to set up a secret key for use by django. This key does not necessarily need to be saved anywhere else.
```
openssl rand -base64 32 > $ELVIS_HOME/config/secret_key
```

You will also need to supply the password for the email account used to send mail to users and the recaptcha private key and save them as `$ELVIS_HOME/config/email_pass` and `$ELVIS_HOME/config/recaptch_priv_key`. The values needed for these files can be found on the wiki (TODO: CREATE A WIKI) or on the live production server.

Back to the database. Create a new role with the name `elvisdb` and the password stored in `$ELVIS_HOME/config/db_pass`. Then, create a database called `elvis_database` with the `elvisdb` role as the owner. You can easily find a step by step guide to do this online if necessary.

## Connecting Solr
Solr can support multiple distinct search indexes running on a single server. Each index's configuration options and data is collectively called a *core*. The elvis-database git repo contains the configuration information for two cores, of which only one is needed. Solr has a home directory, which it searches for cores to load when started. In order to make solr aware of our elvis core, we need to link it in to the `$SOLR_HOME` directory.  You can find where `$SOLR_HOME` is located by running `cat /etc/default/solr.in.sh | grep SOLR_HOME`. Mine is in `/var/solr/data`. In order to link the configuration files used by elvis to solr, run the following. Creating a link is preferred to actually copying the files, as updates to the core configuration will be automatically read by solr.
```
sudo ln -s $ELVIS_HOME/elvis-database/solr/elvisdb $SOLR_HOME
```
You will also need to create a data directory and allow solr to access it. To do this, we will add the solr user to the `elvisdb` group, create a data directory in the core, and give full permissions to group members on that directory.
```
sudo usermod -a -G elvisdb solr
mkdir $ELVIS_HOME/elvis-database/solr/elvisdb/data
chmod 775 $ELVIS_HOME/elvis-database/solr/elvisdb/data
```
In order to assure that everything has worked, restart solr, then run an empty search on the new core. You should get a short response with an empty array of results in it (since we haven't added anything to our index yet.)
```
sudo systemctl restart solr
curl localhost:8983/solr/elvisdb/select?wt=json&q=*:*
# Short json response with empty results.
```

## Populating postgres and solr.
By now, the major parts required to run the project are in place. We can test that postgres is hooked up by creating the tables in the database using django's management tool.

```
# If not already...
cd $ELVIS_HOME/elvis-database
source .env/bin/activate

# Then:
python manage.py migrate
```

If this command fails, you will need to figure out some error in your database setup up or your `$ELVIS_HOME/elvis-database/elvis/settings.py` file.

You must now obtain a dump of the database and a set of its media files. These can be found on our [backup server](http://132.206.14.10/doku.php?id=backups:start), as well as on the production server.

Move all the media folders (`attachments`, `user_downloads`, etc) to `$ELVIS_HOME/media/`. You also want to set all the files to have 664 permissions. You can do this with a command like `find $ELVIS_HOME/media -type f -exec chmod 644 {} \;`. Note, we can not simply run `chmod -R` on this directory tree, as we don't want to remove the executable permission from directories.

You should also have a .json dump of the database available. You can load this into postgres using djangos management utility. Assuming the backup is in your home folder and named `elvis_backup.json`, run the following from `$ELVIS_HOME`.

```
python manage.py loaddata ~/elvis_backup.json
```

This should run without error if you have run the migrations mentioned directly above. 

Lastly, once the `loaddata` command has finished, we can index all the data in solr using the command:

```
python manage.py reindex_all
```

Now our postgres database and solr index are filled with stuff!

### Setting up supervisor 
Before you can run anything using supervisor, you need to create the following directories, to be used by the processes supervisor will be managing.

```
# Make a directory where log files for all processes can reside.
sudo mkdir /var/log/elvisdb
sudo chown elvisdb:elvisdb /var/log/elvisdb

# Make a directory where .pid files and sockets can reside.
sudo mkdir /run/elvisdb
sudo chown elvisdb:elvisdb /run/elvisdb
```
Supervisor is used to manage and control the execution of script files. The elvis database git repository comes with two scripts called `gunicorn_start.sh` and `celery_start.sh`, which supervisor will be responsible for running. These two scripts 'run' the project, supervisor makes sure these two scripts are always running, and nginx points internet requests at the processes started by these scripts. You should have a look at the two scripts if you'd like to know how gunicorn and celery are configured.

To tell supervisor to run these scripts, we need to create a file in supervisor's config folder. In `/etc/supervisor/conf.d`, create a file called `elvisdb.conf` with the following contents:
```
[program:elvisdb]
command=/srv/webapps/elvisdb/elvis-database/gunicorn_start.sh
autostart=true
autorestart=true
stdout_logfile=/var/log/elvisdb/gunicorn.log
redirect_stderr=true
stdout_logfile_maxbytes=50MB

[program:elvisdb-celery]
command=/srv/webapps/elvisdb/elvis-database/celery_start.sh
user=elvisdb
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/elvisdb/celery.log
stdout_logfile_maxbytes=50MB
killasgroup=true
numprocs=1
```
Now, run the supervisor server and start both your new processes.
```
sudo supervisorctl
supervisor> reload
```

That should be about it! If you look at the config file, you'll notice all we're doing is telling supervisor to run the scripts that came with the project, to automatically start them and attempt to restart them if the crash, and where to log their stdout and stderr.


## Setting up nginx
nginx should be already running as it has been installed when you downloaded all the dependencies. You can check that it is running using `sudo systemctl status nginx`. 

We save site definitions in `/etc/nginx/sites-available`, then make a link to the sites we wish to actually serve in `/etc/nginx/sites-enabled`.

Save the following into a file called `/etc/nginx/sites-available/database.elvisproject.ca`.
```
upstream elvisdb_server {
  server unix:/var/run/elvisdb.sock fail_timeout=0;
}

server {
    listen 80;
    server_name database.elvisproject.ca;
    client_max_body_size 4G;

    access_log /var/log/elvisdb/nginx-access.log;
    error_log /var/log/elvisdb/nginx-error.log;

    location /static/ {
        alias   /srv/webapps/elvisdb/static/;
    }

    location /media_serve/ {
        internal;
        alias /srv/webapps/elvisdb/media/;
    }

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        # proxy_buffering off;
        proxy_pass http://elvisdb_server;
    }
}
```

This is a fairly simple config, which takes requests on port 80 and sends them to the socket opened up by gunicorn (you may have noticed the location of this socket being defined in `$ELVIS_HOME/gunicorn_start.sh`). If a static or media file is being requested, nginx will serve it straight off the file system without having to clog up a thread in the web app. Note the 'internal' keyword for the `/media_serve/` location. This means this point can only be accessed by requests that originate from the server itself. We use this to check that a user is logged in when they access a point under `/media/`, then redirect their request to `/media_serve/`.
Note also that encryption is not handled anywhere in this config file. We deploy the elvis database on a server without a public IP. Traffic is directed to it through a routing server on the same network which handles encryption with clients.

Now, link this new config file in `sites-enabled`, run a config test, and reload the nginx service to check if everything is ok.
```
> cd /etc/nginx/sites-enabled
> sudo ln -s /etc/nginx/sites-available/database.elvisproject.ca 
> sudo service nginx configtest
 * Testing nginx configuration
   ...done.
> sudo service nginx reload
```

If for whatever reason the configtest fails, you will find the errors it raised in `/var/log/nginx/error.log`. Use this output to debug your configuration!

# Extra: Moving data to mounted storage.

After deploying the server, we had the need to move all the data on the server to an externally mounted storage drive. This was to simplify the process of redeploying and making backups of all data.

To see the list of external drives mounted at startup, open `/etc/fstab` in a text editor. On the elvis production server, you will notice `/dev/vdc` is mounted to `/media` at startup. This is our external drive. Here you can find all the media files for the database, as well as the data stores for postgres and solr.

The solr data location can be changed simply by shutting down solr, moving the data store, and changing the key `dataDir` in `solrconfig.xml` of every solr core to point to the new location.

[Here is a nice guide for moving the postgres data store](https://www.digitalocean.com/community/tutorials/how-to-move-a-postgresql-data-directory-to-a-new-location-on-ubuntu-16-04).

# Conclusion
After completing these steps, you should have a fully functional elvis database deployment. You will still need to point the DNS record to the new server's IP in order to access the site online, but that is beyond the scope of this guide.
