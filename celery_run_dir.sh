#!/bin/bash

PID_ROOT=/var/run/celery
# Check for existence of pid directory
if [ ! -d "$PID_ROOT" ];then
        mkdir "$PID_ROOT"
        chown celery:celery "$PID_ROOT"
fi

