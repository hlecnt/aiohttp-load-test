#!/bin/bash

USERS=${USERS:-500}
SPAWN=${SPAWN:-10}

UID="$(id -u)"
GID="$(id -g)"
RUNTIME="2m"

AIOHTTP=3.7.3

for COMMIT in 2b3d85d56b09388f40cee03b48343366c9eb3d75 f10987a636d9f054f2eb2cdd8afb8937eaba9726 74d372918c932e23f33ad7ffc2b863a8d008ff14 69de6fe9f098ca51637d1269783e734dca0f9a34 a0cbeb9695dff13cbce5556f563c43bf9079af60 4af0ef51b7b6a5b822821565238568ac4a9f17df 02bf9272cbe359478a6f765b278434e2d1a58600 66f4aed9d67af699a2521067041895d5ad9bcf9d 5996f85b84cfeeed3a8b0c93f1530e6fb973fe1f c4afc95245fe05da17ced5ec2535bf7391fc48e9 42252f154f56149f5e6127fd6fb75cc7cbda8d4e 31fa280bc905227687fce049e2f70de3c4e27053; do
  for PYTHON in 3.6.12; do
    for FLAVOR in buster; do
      for EVENTLOOP in asyncio; do
        docker-compose down && COMMIT=${COMMIT} TARGETHOST=source-server UID=${UID} GID=${GID} USERS=${USERS} SPAWN=${SPAWN} RUNTIME=${RUNTIME} AIOHTTP=${AIOHTTP} PYTHON=${PYTHON} FLAVOR=${FLAVOR} EVENTLOOP=${EVENTLOOP} docker-compose up --build --scale source-server=1 --scale proxied=10 --abort-on-container-exit locust source-server proxied
      done
    done
  done
done
