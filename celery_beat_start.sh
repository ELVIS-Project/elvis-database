#!/bin/bash

# Virtual env path
VIRTUAL_ENV=/srv/webapps/elvis-database/elvis_virtualenv
PROJECT_PATH=/srv/webapps/elvis-database/elvis
# Activate
source ${VIRTUAL_ENV}/bin/activate
# Move to project directory
cd ${PROJECT_PATH}
# Run your scheduled tasks using beat
exec celery -A elvis beat -l info --pidfile="/run/celery/%n.pid" --schedule="/run/celery/celerybeat-schedule"
