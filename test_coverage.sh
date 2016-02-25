#!/bin/bash

# Don't include the virtualenv or the migrations code in coverage
coverage run --omit=.env/*,elvis/migrations/*  manage.py test
coverage html
coverage report
