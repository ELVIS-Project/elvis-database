#!/usr/bin/env bash

source elvis_env/bin/activate
cd /home/lexpar/Documents/DDMAL/elvis-database/elvis/
celery -A elvis worker -l info
