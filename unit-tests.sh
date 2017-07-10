#!/bin/sh

set -ev

grunt test-js
python manage.py migrate --fake-initial
pytest --cov
flake8 fr_notices regulations
bandit -r --ini tox.ini fr_notices regulations manage.py setup.py
