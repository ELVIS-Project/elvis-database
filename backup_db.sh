#!/usr/bin/env bash

#This script is run by root every night at midnight using crontab
#It backs up the database and media files on my macmini in the lab. 
cd /srv/webapps/elvis-database/
source elvis_virtualenv/bin/activate
DATE=$(date +%F)
python manage.py dumpdata --natural-foreign --exclude contenttypes --exclude auth.permission > ../elvis-database-backups/$(echo $DATE).json
rsync -r ../elvis-database-backups/ AlexPar@132.206.14.118:~/ELVISDB_BACKUP
rsync -r ./media_root/ AlexPar@132.206.14.118:~/ELVISDB_BACKUP/media

