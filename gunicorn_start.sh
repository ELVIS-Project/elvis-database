#!/bin/bash

NAME="elvisdb"                                             # name of the application
VIRTUAL_ENV=/srv/webapps/elvisdb/elvis-database/.env       # name of virtual_env directory
DJANGODIR=/srv/webapps/elvisdb/elvis-database/             # Django project directory
SOCKFILE=/var/run/elvisdb/elvisdb.sock                     # we will communicte using this unix socket
USER=elvisdb                                               # the user to run as
GROUP=elvisdb                                              # the group to run as
NUM_WORKERS=3                                              # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=elvis.settings                      # which settings file should Django use
DJANGO_WSGI_MODULE=elvis.wsgi                              # WSGI module name

echo "Starting $NAME"

# Activate the virtual environment
cd $DJANGODIR
source ${VIRTUAL_ENV}/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
#RUNDIR=$(dirname $SOCKFILE)
#test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec ${VIRTUAL_ENV}/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --log-level=warnin \
  --bind=unix:$SOCKFILE
