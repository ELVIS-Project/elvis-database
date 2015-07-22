#!/bin/bash

# Virtual env path
VIRTUAL_ENV=/usr/local/elvis-database/elvis_virtualenv
PROJECT_PATH=/usr/local/elvis-database/elvis
# Activate
source ${VIRTUAL_ENV}/bin/activate
# Move to project directory
cd ${PROJECT_PATH}
# Run your worker... old: exec celery worker -A elvis -l DEBUG --loglevel=INFO 
exec celery worker -A elvis -l info --pidfile="/run/celery/%n.pid"
