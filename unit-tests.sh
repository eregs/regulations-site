#!/bin/sh

set -ev

grunt test-js
python manage.py migrate --fake-initial
python manage.py test
flake8 .
bandit -r .
