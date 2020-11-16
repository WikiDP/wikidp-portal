#!/usr/bin/env bash
source ./venv/bin/activate
# Wikidp production token
export CONSUMER_TOKEN=''
export SECRET_TOKEN=''
export FLASK_APP='wikidp'
flask run
