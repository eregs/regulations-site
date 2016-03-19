#!/bin/sh

set -ev

./dummy_api/start.sh
echo 'API_BASE = "http://localhost:8282/"' >> local_settings.py
./run_server.sh &
sleep 5
grunt nose
