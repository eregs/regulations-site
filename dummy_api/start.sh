#!/bin/bash
docker run -p 8282:8080 --name core -d eregs/core
# Sleep for 5 to give Django enough time to start up
sleep 5

# Load dummy data (@todo - replace with real data)
for TAIL in $(find */* -type f | sort -r)
do
    curl -X PUT http://localhost:8282/$TAIL -d @$TAIL
done

# Load a real notice
mkdir cache
docker run --rm -it -v $PWD/cache:/app/cache eregs/parser notice_preamble 2016-02749
docker run --rm -it -v $PWD/cache:/app/cache eregs/parser layers
docker run --rm -it -v $PWD/cache:/app/cache --link core:core eregs/parser write_to http://core:8080

docker logs core
