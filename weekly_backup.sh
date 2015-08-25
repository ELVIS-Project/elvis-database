#!/usr/bin/env bash

python manage.py dumpdata --natural-foreign --exclude contenttypes --exclude auth.permission > ../elvis-database-backups/daily/$(echo $DATE).json
ssh AlexPar@132.206.14.118 'cd ~/ELVISDB_BACKUP/; rm -rf backup.3; mv backup.2 backup.3; mv backup.1 backup.2; mv backup.0 backup.1;'
rsync -r /srv/webapps/elvis-database/media_root/ /srv/webapps/elvis-database-backups/backup.0
rsync -a --delete --link-dest=AlexPar@132.206.14.118:~/ELVISDB_BACKUP/backup.1 /srv/webapps/elvis-database-backups/backup.0/ AlexPar@132.206.14.118:~/ELVISDB_BACKUP/backup.0
