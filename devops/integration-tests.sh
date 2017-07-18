#!/bin/bash
set -ev
export COMPOSE_FILE='./devops/integration-tests.yml'
export COMPOSE_PROJECT_NAME='integrationtests'

docker-compose up -d api
# Sleep for 5 to give Django enough time to start up
sleep 5

cd devops/dummy_api
# Load dummy data (@todo - replace with real data)
for TAIL in $(find */* -type f | sort -r)
do
    curl -X PUT http://localhost:8080/$TAIL -d @$TAIL
done
cd ../..

# Set-up and migrate parser database
docker-compose run --rm --entrypoint ./manage.py parser migrate
PARSER="docker-compose run --rm parser"
# Load a real notice
$PARSER notice_preamble 2016-02749
$PARSER layers
$PARSER write_to http://api:8080

# Modify the close date
curl http://localhost:8080/notice/2016-02749 | python -m json.tool > notice.json
FUTURE=`date --date="1 month" +"%Y-%m-%d"`
sed -i "s/2016-04-29/$FUTURE/g" notice.json
curl -X PUT http://localhost:8080/notice/2016-02749 -d @notice.json
rm notice.json

if [ "$TRAVIS_PYTHON_VERSION" = "2.7" ]
then docker-compose up -d site2
else docker-compose up -d site3
fi
sleep 5
export UITESTS_URL=http://localhost:8000
UITESTS_REMOTE=chrome tox -e integration
UITESTS_REMOTE=ie11 tox -e integration

docker-compose down -v
