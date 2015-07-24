#Current Deployment

Here are a few notes on the deployment of the website on July 24, 2015.

##Django configuration

The Django webapp is located in /usr/local/elvis-database.

Secret key and email password for the webapp are being stored in /etc/elvis_secretkey.txt and /etc/elvis_emailpass.txt.

The webapp is using the postgresql db named `elvis2`, owned by user `elvisdatabase` with password `5115C67O2v3GN31T49Md`
A db named `elvisdatabase` exists which contains the unmigrated contents of the database before this deployment.


##Solr configuration

The solr Collection is in `/usr/local/elvis-database/solr/`
The solr DataDir is `/var/db/elvis-solr2`.
The solr webapp is being served by tomcat from `/usr/share/tomcat/webapps/elvis-solr.war`

##Celery

Celery is being managed by supervisor. It has two tasks defined in `/etc/supervisord.conf` that run the scripts
`/usr/local/elvis-database/celery_start.sh` and `/usr/local/elvis-database/celery_beat_start.sh`