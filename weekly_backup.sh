#!/usr/bin/env bash
#This should keep a month of backups availiable at all times.

cd /srv/webapps/elvis-database/
source elvis_virtualenv/bin/activate
DATE=$(date +%F)
echo Backing up locally to /srv/webapps/elvis-database-backups/backup.0
rsync -r --delete /srv/webapps/elvis-database/media_root/ /srv/webapps/elvis-database-backups/backup.0

echo Dumping database to JSON.
python manage.py dumpdata --natural-foreign --exclude contenttypes --exclude auth.permission > ../elvis-database-backups/backup.0/$(echo $DATE).json

echo Preparing remote server...
ssh AlexPar@132.206.14.118 'cd ~/ELVISDB_BACKUP/; rm -rf backup.3; mv backup.2 backup.3; mv backup.1 backup.2; cp -r backup.0 backup.1;'

echo Synching to remote server...
rsync -r --delete /srv/webapps/elvis-database-backups/backup.0/ AlexPar@132.206.14.118:~/ELVISDB_BACKUP/backup.0/
echo Done! $Date weekly backup complete.
