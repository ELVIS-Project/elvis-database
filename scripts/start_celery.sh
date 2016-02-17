#!/usr/bin/env bash

cd /home/lexpar/Documents/DDMAL/elvis-database/
celery -A elvis worker -l info
