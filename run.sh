#!/usr/bin/env bash
source ./venv/bin/activate
export WIKIDP_BOT_USER='<username>'
export WIKIDP_BOT_PASSWORD='<password>'
export FLASK_APP='wikidp/__init__.py'
flask run
