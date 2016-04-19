#!/bin/sh

set -ev

./dummy_api/start.sh
cp local_settings_test.py local_settings.py
./run_server.sh &
sleep 5
grunt nose
