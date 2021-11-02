#!/bin/bash

USERS=${USERS:-500}
SPAWN=${SPAWN:-10}

UID="$(id -u)"
GID="$(id -g)"
RUNTIME="2m"

CT_TOTAL=${CT_TOTAL:-1}
CT_CONNECT=${CT_CONNECT:-0.5}
CT_SOCK_CONNECT=${CT_SOCK_CONNECT:-0.5}


#RUNTIME="5s"
#USERS=1
#SPAWN=1

CT_TOTAL=0
CT_CONNECT=0
CT_SOCK_CONNECT=0

EVENTLOOP=asyncio

PYTHON=3.6.12
FLAVOR=buster
AIOHTTP=3.4.2
TARGETHOST=spied-server
docker-compose down && \
  UID=${UID} GID=${GID} \
  USERS=${USERS} \
  SPAWN=${SPAWN} \
  RUNTIME=${RUNTIME} \
  AIOHTTP=${AIOHTTP} \
  PYTHON=${PYTHON} \
  FLAVOR=${FLAVOR} \
  EVENTLOOP=${EVENTLOOP} \
  TARGETHOST=${TARGETHOST} \
  CT_TOTAL=${CT_TOTAL} \
  CT_CONNECT=${CT_CONNECT} \
  CT_SOCK_CONNECT=${CT_SOCK_CONNECT} \
  docker-compose up --build --scale server=0 --scale spied-server=1 --scale proxied=10 --abort-on-container-exit
cp profile.svg ${PYTHON}-${FLAVOR}-${AIOHTTP}-${EVENTLOOP}.svg

PYTHON=3.6.12
FLAVOR=buster
AIOHTTP=3.7.3
TARGETHOST=spied-server
docker-compose down && \
  UID=${UID} GID=${GID} \
  USERS=${USERS} \
  SPAWN=${SPAWN} \
  RUNTIME=${RUNTIME} \
  AIOHTTP=${AIOHTTP} \
  PYTHON=${PYTHON} \
  FLAVOR=${FLAVOR} \
  EVENTLOOP=${EVENTLOOP} \
  TARGETHOST=${TARGETHOST} \
  CT_TOTAL=${CT_TOTAL} \
  CT_CONNECT=${CT_CONNECT} \
  CT_SOCK_CONNECT=${CT_SOCK_CONNECT} \
  docker-compose up --build --scale server=0 --scale spied-server=1 --scale proxied=10 --abort-on-container-exit
cp profile.svg ${PYTHON}-${FLAVOR}-${AIOHTTP}-${EVENTLOOP}.svg
