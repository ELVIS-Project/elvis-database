#!/usr/bin/env bash

BASE_DIR="/srv/webapps/elvisdb"

# Save a backup
mv "${BASE_DIR}/dev" "${BASE_DIR}/old/dev_$(date +%s)"

# Clone the repo
git clone -b dev git@github.com:ELVIS-Project/elvis-database.git ${BASE_DIR}/dev

# Set up the virtualenv
virtualenv -p python3 ${BASE_DIR}/dev/.env

# Install requirements
source ${BASE_DIR}/dev/.env/bin/activate
pip install -r ${BASE_DIR}/dev/requirements.txt

# Perform Django management tasks
python ${BASE_DIR}/dev/manage.py collectstatic --noinput
python ${BASE_DIR}/dev/manage.py migrate --noinput

# Restart supervisor processes
sudo supervisorctl restart elvis-db-dev
sudo supervisorctl restart elvis-celery-dev

echo "Elvis DB Dev Deployment Complete"