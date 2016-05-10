#!/usr/bin/env bash

#This script is run by root every night at midnight using crontab
#It backs up the database and media files on my macmini in the lab.
cd /srv/webapps/elvisdb/prod
source .env/bin/activate
DATE=$(date +%F)

echo Dumping database to /srv/webapps/elvis-database/db_dumps
python manage.py dumpdata --natural-foreign --exclude contenttypes --exclude auth.permission > ../../elvis-database-backups/db_dumps/$(echo $DATE).json

# Deletes any daily dumps older than 30 days.
cd /srv/webapps/elvis-database-backups/db_dumps/
ls -tp | grep -v '/$' | tail -n +30 | xargs -I {} rm -- {}

echo Synching to remote server...
cd /srv/webapps/
rsync -r ./elvis-database-backups/db_dumps AlexPar@132.206.14.118:~/ELVISDB_BACKUP/db_dumps
rsync -r ./elivsdb_media/prod/ AlexPar@132.206.14.118:~/ELVISDB_BACKUP/media
echo $DATE nightly back-up succesful!
