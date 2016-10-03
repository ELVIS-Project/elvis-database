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

* python3
* python3-dev
* git
* build-essential
* virtualenv
* postgreSQL
    - Database implementation (technically any SQL database would work.)

You can install all of the above on Ubuntu using the following command:
```
sudo apt install python3 python3-dev git virtualenv postgres 
```

In addition to the above, you will need to install the following services manually.
* rabbitmq
    - Message passer used by celery.
* solr
    - Fast search engine which powers the site's search feature.
* redis
    - In memory key-value based cache.
    
# Setup
We need to set up the deployment directory.
```
sudo mkdir -p /srv/webapps/elvisdb/{config,media,static}
sudo chown elvisdb:elvisdb /srv/webapps/elvisdb
```

From now on, I will refer to `/srv/webapps/elvisdb` as `$ELVISHOME`

*Note: on the active deployment of the production server, a file named /home/elvisdb/elvis-env.sh contains a list of these variables and their definitions.*

While in `$ELVISHOME`, run the following command

