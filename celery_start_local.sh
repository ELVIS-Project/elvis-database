#!/bin/bash

source .env/bin/activate
exec celery worker -A elvis -l info -Q elvis-local
