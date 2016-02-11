#!/usr/bin/env bash

# Clone the repo
git clone -b dev git@github.com:ELVIS-Project/elvis-database.git ../dev_deploy

# Set up the virtualenv
virtualenv -p python3 ../dev_deploy/.env

# Install requirements
source ../dev_deploy/.env/bin/activate
pip install -r ../dev_deploy/requirements.txt

