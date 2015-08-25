#!/usr/bin/env bash

#This script is run by root every night at midnight using crontab
#It backs up the database and media files on my macmini in the lab.
cd /srv/webapps/elvis-database/
source elvis_virtualenv/bin/activate
DATE=$(date +%F)

echo Dumping database to /srv/webapps/elvis-database/db_dumps
python manage.py dumpdata --natural-foreign --exclude contenttypes --exclude auth.permission > ../elvis-database-backups/db_dumps/$(echo $DATE).json

# Deletes any daily dumps older than 50 days.
ls ../elvis-database-backups/db_dumps -t | sed -e '1,50d' | xargs -d '\n' rm

echo Synching to remote server...
rsync -r ../elvis-database-backups/db_dumps AlexPar@132.206.14.118:~/ELVISDB_BACKUP/db_dumps
rsync -r ./media_root/ AlexPar@132.206.14.118:~/ELVISDB_BACKUP/media
echo $DATE nightly back-up succesful!
