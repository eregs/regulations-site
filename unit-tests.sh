#!/bin/sh

set -ev

grunt test-js
python manage.py migrate --fake-initial
pytest --cov
flake8 .
bandit -r . -x node_modules,regulations/tests,fr_notices/tests,regulations/uitests
