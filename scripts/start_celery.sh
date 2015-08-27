#!/usr/bin/env bash

cd /home/lexpar/Documents/DDMAL/elvis-database/elvis/
celery -A elvis worker -l info
