#!/usr/bin/env bash

source elvis_virtualenv/bin/activate
DATE=$(date +%F)
python manage.py dumpdata --natural-foreign --exclude contenttypes --exclude auth.permission > ../elvis-database-backups/$(echo $DATE).json
