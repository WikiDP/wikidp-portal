#!/usr/bin/env bash
SCRIPT_DIR="$( dirname "$( readlink -f "${BASH_SOURCE[0]}" )")"
cd "${SCRIPT_DIR}" || exit
pip install -U pip
pip install -U -e .
export FLASK_APP='wikidp/__init__.py'
export FLASK_ENV=development
flask run --host 0.0.0.0 --port 5000
