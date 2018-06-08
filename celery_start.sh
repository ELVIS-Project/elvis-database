#!/bin/bash

# Virtual env path
VIRTUAL_ENV=/srv/webapps/elvisdb/elvis-database/.env
PROJECT_PATH=/srv/webapps/elvisdb/elvis-database
# Activate
source ${VIRTUAL_ENV}/bin/activate
# Move to project directory
cd ${PROJECT_PATH}
# Run your worker... old: exec celery worker -A elvis -l DEBUG --loglevel=INFO
exec celery worker -A elvis -l info -Q elvisdb
