#!/usr/bin/env bash

# Opens three tabs in a new terminal window and gets all the processes running for the local server.
gnome-terminal --tab -e "scripts/start_solr.sh" --tab -e "scripts/start_django.sh" --tab -e "scripts/start_celery.sh"