#!/bin/bash

_term() {
  echo "Caught SIGTERM signal!"
  kill -INT ${SPY}
  kill -TERM ${PY}
}

_int() {
  echo "Caught SIGINT signal!"
  kill -INT ${SPY}
  kill -TERM ${PY}
}

trap _term SIGTERM
trap _int SIGINT

python3 -u server.py &
PY=$!

py-spy record -o /mnt/spy/profile.svg -p ${PY} &
SPY=$!

echo "Wait for process termination."
wait
sleep 30
echo "Done."
