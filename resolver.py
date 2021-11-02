import asyncio
import logging
import socket

import aiodns


class Resolver:
    running: bool
    servers: list

    def __init__(self, logger: logging.Logger) -> None:
        self.running = False
        self.resolver = aiodns.DNSResolver()
        self.logger = logger
        self.servers = []

    async def resolver_task(self, hostname: str):
        self.running = True
        while self.running:
            try:
                res = await self.resolver.gethostbyname(hostname, socket.AF_INET)
                self.servers = sorted([ ip for ip in res.addresses ])
                self.logger.debug(f"Resolved addresses for {hostname}={self.servers}")
            except (asyncio.CancelledError, Exception) as e:
                self.logger.error(f"")
            finally:
                await asyncio.sleep(1)
