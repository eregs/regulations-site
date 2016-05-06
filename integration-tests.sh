#!/bin/sh

set -ev

cd dummy_api
./start.sh
cd ..
cp local_settings_test.py local_settings.py
./run_server.sh &
sleep 5
grunt nose
