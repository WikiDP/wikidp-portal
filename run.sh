#!/usr/bin/env bash
source ./venv/bin/activate
# Wikidp production token
# export WIKIDP_CONSUMER_KEY=''
# export WIKIDP_CONSUMER_SECRET=''
export FLASK_APP='wikidp'
flask run
