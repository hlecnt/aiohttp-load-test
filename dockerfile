ARG PYTHON=3.6.12
ARG FLAVOR=buster
FROM python:${PYTHON}-slim-${FLAVOR} AS base
ARG AIOHTTP

RUN mkdir -p /workspace
COPY dependencies.txt /workspace/
COPY resolver.py /workspace/
RUN apt-get update && \
    apt-get install -y build-essential && \
    pip install -r /workspace/dependencies.txt && \
    pip install aiohttp==$AIOHTTP
RUN apt-get remove -y --purge build-essential && \
      apt-get autoremove -y && \
      rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
EXPOSE 80

FROM base AS server
COPY server.py /workspace/
ENTRYPOINT ["/usr/local/bin/python3", "server.py"]

FROM base AS spied-server
RUN pip install py-spy
COPY server.py /workspace/
COPY spied-boot.bash /workspace/
RUN chmod +x /workspace/spied-boot.bash
ENTRYPOINT ["/workspace/spied-boot.bash" ]

FROM base AS client
COPY client.py /workspace/
ENTRYPOINT ["/usr/local/bin/python3", "client.py"]

FROM base AS proxied
COPY proxied.py /workspace/
ENTRYPOINT ["/usr/local/bin/python3", "proxied.py"]