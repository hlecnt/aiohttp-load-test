This is a custom load tester for [AIOHTTP](https://github.com/aio-libs/aiohttp).

The purpose of this load tester is to compare AIOHTTP performance depending on its version.

The tester is based on a docker-compose app having the following services:
- server: the server service under load test. Handles only 'ping' request and forward them to the 'proxied' service.
- proxied: another AIOHTTP server answsering to 'ping' requests.
- locust: the HTTP load tester

At the end of the test, locust create an HTML report in the current directory.

Some environment variables are avaialble to configure the load tester app:
- PYTHON: defines the Python version to use in services. More precisely it's the version of 'python:slim_buster' to use. Defaults to `3.6.12`
- AIOHTTP: defines the AIOHTTP version to use. Defaults to `3.7.3`
- EVENTLOOP: defines the event loop to use. It can be one of `asyncio` or `uvloop`. Defaults to asyncio.
- USERS: defines the number of users that locust will create for its load testing. Defaults to `500`
- SPAWN: defines the locust user spawn rate. Defaults to `10`.
- RUNTIME: defines the locust load test duration. Defaults to `2m`
- UID: your local linux user id for the locust service
- GID: your local linux group id for the locust service

# UID and GID
Don't forget to set UID and GID envrionement variable in order to let locsut create reports with the correct user rights.

# Command line examples

Run the load tester with the default parameters:
```
docker-compose down && docker-compose up --build --scale server=1 --scale proxied=10 --abort-on-container-exit --remove-orphans
```

Run the load tester with overriden envrionement variables:
```
docker-compose down && UID=1017 GID=1018 AIOHTTP=3.4.2 EVENTLOOP=uvloop docker-compose up --build --scale server=1 --scale proxied=10 --abort-on-container-exit --remove-orphans
```

# benchmark
Then `benchmark.sh` can be used to run a set of tests.
```
bash benchmark.sh
```