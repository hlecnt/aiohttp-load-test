import asyncio
import logging
import os
import signal

import resolver
from aiohttp import ClientTimeout, web

try:
    from aiohttp.helpers import get_running_loop
except:
    get_running_loop = asyncio.get_event_loop
from aiohttp import ClientError, ClientSession, TCPConnector

try:
    import uvloop
except:
    pass

MAXIMUM_ALLOWED_CONNECTIONS = 1024

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")


timeout = ClientTimeout(total=1, connect=0.5, sock_connect=0.5)


def signal_term_handler():
    asyncio.get_event_loop().stop()


async def starthttpserver(app: web.Application, host: str, port: int):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port, backlog=MAXIMUM_ALLOWED_CONNECTIONS)
    logger.info(f"Serving on http://{host}:{port}/")
    await site.start()
    return runner, site


async def stophttpserver(runner: web.AppRunner, site: web.TCPSite):
    await site.stop()
    await runner.cleanup()


async def ping(request: web.Request) -> web.StreamResponse:
    logger.info(f"Processing request {request.url}")
    resolv = request.app["resolver"]
    upstream = request.app["upstream_rr"] % len(resolv.servers)
    request.app["upstream_rr"] += 1
    session: ClientSession = request.app["upstream_session"]
    try:
        response = await session.get(
            f"http://{resolv.servers[upstream]}/ping", timeout=timeout
        )
    except (asyncio.CancelledError, ClientError) as ce:
        logger.error(f"GET: {type(ce)}: {str(ce)}")
        return web.json_response({}, status=503)
    try:
        read = await response.json()
        ret = web.json_response(read)
    except (asyncio.CancelledError, ClientError) as ce:
        logger.error(f"READ: {type(ce)}: {str(ce)}")
        return web.json_response({}, status=503)
    finally:
        response.close()
    return ret


if __name__ == "__main__":
    logger.info(f"Starting...")

    try:
        type_of_event_loop = os.environ.get('EVENTLOOP', 'asyncio')
        if type_of_event_loop == 'uvloop':
            uvloop.install()
    except:
        pass
    loop = get_running_loop()
    try:
        logger.info(f"Starting with {'uvloop' if isinstance(loop, uvloop.Loop) else 'asyncio'} event loop")
    except:
        logger.info(f"Starting with asyncio event loop")

    loop.add_signal_handler(signal.SIGTERM, signal_term_handler)

    app = web.Application()

    app.router.add_get("/ping", ping)

    resolv = resolver.Resolver(logger)
    loop.create_task(resolv.resolver_task("proxied"))

    connector = TCPConnector(use_dns_cache=True, ttl_dns_cache=120, force_close=False)
    app["upstream_session"] = ClientSession(connector=connector)
    app["upstream_rr"] = 0
    app["resolver"] = resolv

    logger.info(f"Instantiate HTTP server...")
    runner, site = loop.run_until_complete(
        starthttpserver(app, host="0.0.0.0", port=80)
    )

    logger.info(f"Serving...")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Caught KeyboardInterrupt")
        pass

    loop.run_until_complete(stophttpserver(runner, site))
    logger.info(f"Bye Bye!")
