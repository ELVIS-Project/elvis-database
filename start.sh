#!/usr/bin/env bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd $DIR
source env_3/bin/activate
# Opens three tabs in a new terminal window and gets all the processes running for the local server.
gnome-terminal --tab -e "scripts/start_solr.sh" --tab -e "scripts/start_django.sh" --tab -e "scripts/start_celery.sh"
