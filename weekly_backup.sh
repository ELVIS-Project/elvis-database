#!/usr/bin/env bash

#Weekly full backup script

cd /srv/webapps/elvisdb/prod
source .env/bin/activate
DATE=$(date +%F)

echo Backing up locally to /srv/webapps/elvis-database-backups/backup.0
rsync -r --delete /srv/webapps/elvisdb_media/prod/ /srv/webapps/elvis-database-backups/backup.0

echo Dumping database to JSON.
python manage.py dumpdata --natural-foreign --exclude contenttypes --exclude auth.permission > ../../elvis-database-backups/backup.0/$(echo $DATE).json

echo Preparing remote server...
ssh AlexPar@132.206.14.118 'cd ~/ELVISDB_BACKUP/; rm -rf backup.3; mv backup.2 backup.3; mv backup.1 backup.2; cp -r backup.0 backup.1;'

echo Synching to remote server...
rsync -r --delete /srv/webapps/elvis-database-backups/backup.0/ AlexPar@132.206.14.118:~/ELVISDB_BACKUP/backup.0/
echo Done! $DATE weekly backup complete.
