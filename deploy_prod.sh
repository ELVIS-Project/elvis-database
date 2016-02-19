#!/usr/bin/env bash

ENV="prod"
BASE_DIR="/srv/webapps/elvisdb"

# Save a backup
mv "${BASE_DIR}/${ENV}" "${BASE_DIR}/old/${ENV}_$(date +%s)"

# Clone the repo
git clone git@github.com:ELVIS-Project/elvis-database.git ${BASE_DIR}/${ENV}

# Set up the virtualenv
virtualenv -p python3 ${BASE_DIR}/${ENV}/.env

# Install requirements
source ${BASE_DIR}/${ENV}/.env/bin/activate
pip install -r ${BASE_DIR}/${ENV}/requirements.txt

# Perform Django management tasks
python ${BASE_DIR}/${ENV}/manage.py collectstatic --noinput
python ${BASE_DIR}/${ENV}/manage.py migrate --noinput

# Restart supervisor processes
sudo supervisorctl restart elvis-db-${ENV}
sudo supervisorctl restart elvis-celery-${ENV}

# Permissions
chown $USER:elvisDB ${BASE_DIR}/${ENV}
chmod 775 ${BASE_DIR}/${ENV}

echo "Elvis DB ${ENV} Deployment Complete"