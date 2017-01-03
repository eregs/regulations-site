#!/bin/sh

set -ev

cd dummy_api
./start.sh
cd ..
cp local_settings_test.py local_settings.py
./run_server.sh &
sleep 5
export UITESTS_URL=http://localhost:8000
UITESTS_REMOTE=chrome py.test regulations/uitests -s
UITESTS_REMOTE=ie11 py.test regulations/uitests -s
