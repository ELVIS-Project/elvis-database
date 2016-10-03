# Initialization
We're installing the project on a compute canada virtual machine instance with Ubuntu 16 installed. If installing on a different environment, the only real requirement is that the OS is POSIX compliant and that all the software listed in the 'Required Software' section can run on it.

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

If your system does not have nice shell defaults for new users, you might be able to grab some from the Ubuntu user (this may be very particular to Compute Canada).
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
sudo apt install python3 python3-dev python-software-properties git virtualenv postgresql-client oracle-java8-installer libpq-dev  libncurses5-dev build-essential supervisor tcl nginx
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
3. You can verify the above worked by running `curl localhost:8983/solr/`. If everything is working, it will return a lengthy html response. You can also use `sudo systemctl status solr` to check the status of the new daemon.

## supervisor
You should have installed supervisor via the ubuntu package manager in the above section. In order to assure it is running, run `sudo systemctl status supervisor`. If it is not running, you may need to enable the service by running `sudo systemctl enable supervisor`. If these commands read like witchcraft, you may want to learn the [bare minimum about systemd.](https://www.digitalocean.com/community/tutorials/systemd-essentials-working-with-services-units-and-the-journal) 

## redis
redis is an in memory key-value based cache. You can find installation instructions at http://redis.io/

At the time of writing, a nice guide for installing redis is available at https://www.digitalocean.com/community/tutorials/how-to-install-and-use-redis
    
# Setup
We need to set up the deployment directory.
```
sudo mkdir -p /srv/webapps/elvisdb/{config,media,static}
sudo chown elvisdb:elvisdb /srv/webapps/elvisdb
```

From now on, I will refer to `/srv/webapps/elvisdb` as `$ELVISHOME`

*Note: on the active deployment of the production server, a file named /home/elvisdb/elvis-env.sh contains a list of these variables and their definitions.*

While in `$ELVISHOME`, run the following command:
```
git clone https://github.com/ELVIS-Project/elvis-database.git
```

This will create a directory `$ELVISHOME/elvis-database/`. Lets go into this directory and create a python 3 virtual environment, source it, and install the project's python requirements.
```
cd $ELVISHOME/elvis-database/
virtualenv --python=python3 .env
source .env/bin/activate
pip install -r requirements.txt
```

Lastly, we need to change one setting in the project configuration file to make it aware that we are doing a production deployment. Open up $ELVISHOME/elvis-database/elvis/settings.py, and change the`SETTING_TYPE` variable from `LOCAL` to `PRODUCTION`.

Now the basic environment for the project is set up, we can begin connecting the various components together.

## Connecting Solr
Solr can support multiple distinct search indexes running on a single server. Each index's configuration options and data is collectively called a *core*. The elvis-database git repo contains the configuration information for two cores, of which only one is needed. Solr has a home directory, which it searches for cores to load when started. In order to make solr aware of our elvis core, we need to link it in to the `$SOLR_HOME` directory.  You can find where `$SOLR_HOME` is located by running `cat /etc/default/solr.in.sh | grep SOLR_HOME`. Mine is in `/var/solr/data`. In order to link the configuration files used by elvis to solr, run the following. Creating a link is preferred to actually copying the files, as updates to the core configuration will be automatically read by solr.
```
sudo ln -s $ELVISHOME/elvis-database/solr/elvisdb $SOLR_HOME
```
You will also need to create a data directory and allow solr to access it. To do this, we will add the solr user to the `elvisdb` group, create a data directory in the core, and give full permissions to group members on that directory.
```
sudo usermod -a -G elvisdb solr
mkdir $ELVISHOME/elvis-database/solr/elvisdb/data
chmod 775 $ELVISHOME/elvis-database/solr/elvisdb/data
```
In order to assure that everything has worked, restart solr, then run an empty search on the new core. You should get a short response with an empty array of results in it (since we haven't added anything to our index yet.)
```
sudo systemctl restart solr
curl localhost:8983/solr/elvisdb/select?wt=json&q=*:*
# Short json response with empty results.
```

## Connecting postgreSQL
The project expects there to be a postgreSQL database called `elvis_database` owned by a user named `elvisdb` with a password stored in `$ELVISHOME/config/db_pass`.

First, lets generate a password and save it in `$ELVISHOME/config/db_pass`. You can use any password you like, but a long, random one is best. You should make sure to save this password offsite. One way to generate a password:
```
openssl rand -base64 32 > $ELVISHOME/config/db_pass
```

Now is also a good time to set up a secret key for us by django. This key does not necessarily need to be saved anywhere else.
```
openssl rand -base64 32 > $ELVISHOME/config/secret_key
```

You will also need to supply the password for the email account used to send mail to users and the recaptcha private key and save them as `$ELVISHOME/config/email_pass` and `$ELVISHOME/config/recaptch_priv_key`. The values needed for these files can be found on the wiki (TODO: CREATE A WIKI) or on the live production server.
