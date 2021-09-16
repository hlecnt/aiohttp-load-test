import asyncio
import logging
import os
import platform
import signal

from aiohttp import web

try:
    from aiohttp.helpers import get_running_loop
except:
    get_running_loop = asyncio.get_event_loop

try:
    import uvloop
except:
    pass


MAXIMUM_ALLOWED_CONNECTIONS = 1024

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(platform.node())


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
    return web.json_response({})


if __name__ == "__main__":
    logger.info(f"Starting...")

    try:
        type_of_event_loop = os.environ.get("EVENTLOOP", "asyncio")
        if type_of_event_loop == "uvloop":
            uvloop.install()
    except:
        pass
    loop = get_running_loop()
    try:
        logger.info(
            f"Starting with {'uvloop' if isinstance(loop, uvloop.Loop) else 'asyncio'} event loop"
        )
    except:
        logger.info(f"Starting with asyncio event loop")

    loop.add_signal_handler(signal.SIGTERM, signal_term_handler)

    app = web.Application()

    app.router.add_get("/ping", ping)

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
