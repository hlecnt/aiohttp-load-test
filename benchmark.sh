#!/bin/bash

USERS=${USERS:-500}
SPAWN=${SPAWN:-10}

UID="$(id -u)"
GID="$(id -g)"
RUNTIME="2m"

for AIOHTTP in 3.4.2 3.8.0; do
  for PYTHON in 3.6.12 3.8.12 3.9.7; do
    for FLAVOR in buster bullseye; do
      for EVENTLOOP in asyncio uvloop; do
        docker-compose down && UID=${UID} GID=${GID} USERS=${USERS} SPAWN=${SPAWN} RUNTIME=${RUNTIME} AIOHTTP=${AIOHTTP} PYTHON=${PYTHON} FLAVOR=${FLAVOR} EVENTLOOP=${EVENTLOOP} docker-compose up --build --scale server=1 --scale proxied=10 --abort-on-container-exit server proxied locust
      done
    done
  done
done
