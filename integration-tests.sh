#!/bin/sh

set -ev

cd dummy_api
./start.sh
cd ..
cp local_settings_test.py local_settings.py
if [ "$TRAVIS_PYTHON_VERSION" = "2.7" ]
then docker build . -t eregs/site --build-arg PYTHON3=''
else docker build . -t eregs/site --build-arg PYTHON3=3
fi
docker run --rm -p 8000:8000 -d eregs/site
sleep 5
export UITESTS_URL=http://localhost:8000
UITESTS_REMOTE=chrome tox -e integration
UITESTS_REMOTE=ie11 tox -e integration
