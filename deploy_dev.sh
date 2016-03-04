#!/usr/bin/env bash

ENV="dev"
BASE_DIR="/srv/webapps/elvisdb"

printf "Beginning ${ENV} Deployment\n"

printf "Dumping database to disk.  This may take a while...\n"

# Dump the database
source ${BASE_DIR}/${ENV}/.env/bin/activate
python ${BASE_DIR}/${ENV}/manage.py dumpdata > ${BASE_DIR}/${ENV}/database_$(date +%s).json
deactivate

printf "Saving code backup...\n"

# Save a backup
mv "${BASE_DIR}/${ENV}" "${BASE_DIR}/old/${ENV}_$(date +%s)"

printf "Cloning repo from GitHub...\n"

# Clone the repo
git clone -b dev git@github.com:ELVIS-Project/elvis-database.git ${BASE_DIR}/${ENV}

printf "Installing Python requirements...\n"

# Set up the virtualenv
virtualenv -p python3 ${BASE_DIR}/${ENV}/.env

# Install requirements
source ${BASE_DIR}/${ENV}/.env/bin/activate
pip install -r ${BASE_DIR}/${ENV}/requirements.txt

printf "Performing Django management tasks...\n"

# Perform Django management tasks
python ${BASE_DIR}/${ENV}/manage.py collectstatic --noinput
python ${BASE_DIR}/${ENV}/manage.py migrate --noinput

# Clear the Cache
python ${BASE_DIR}/${ENV}/manage.py clear_cache

printf "Starting application processes...\n"

# Restart supervisor processes
sudo supervisorctl restart elvis-db-${ENV}
sudo supervisorctl restart elvis-celery-${ENV}

printf "File system cleanup...\n"

# Permissions
chown $USER:elvisDB ${BASE_DIR}/${ENV}
chmod 775 ${BASE_DIR}/${ENV}

printf "Elvis DB ${ENV} Deployment Complete\n"
