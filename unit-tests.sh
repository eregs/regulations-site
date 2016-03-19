#!/bin/sh

set -ev

grunt test-js
python manage.py test
flake8 .
