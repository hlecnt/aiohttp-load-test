import asyncio
import logging
import os
import platform
import statistics
import time
from collections import Counter
from typing import Optional

import aiohttp

try:
    from aiohttp.helpers import get_running_loop
except:
    get_running_loop = asyncio.get_event_loop
from aiohttp import ClientError, ClientSession

try:
    import uvloop
except:
    pass

MAXIMUM_ALLOWED_CONNECTIONS = 1024

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(platform.node())


def signal_term_handler():
    asyncio.get_event_loop().stop()


async def ping(session: ClientSession, url: str) -> Optional[aiohttp.ClientResponse]:
    response = None
    logger.info(f"Sending request {url}...")
    try:
        response = await session.get(url)
    except (asyncio.CancelledError, ClientError) as ce:
        logger.error(f"{type(ce)}: {str(ce)}")
    if response is not None:
        response.close()
    return response


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

    session = ClientSession()

    # wait for services to be up and running
    ret = None
    servers = ["server"]
    for s in servers:
        while True:
            try:
                ret = loop.run_until_complete(ping(session, f"http://{s}/ping"))
                if ret != None and ret.status == 200:
                    break
            except (asyncio.CancelledError, ClientError) as ce:
                pass
            logger.warning(
                f"Service {s} is not yet ready, status={ret.status if ret else 'N/A'}"
            )
            loop.run_until_complete(asyncio.sleep(1))

    # Additional wait for first hostname resolution in 'server' service
    loop.run_until_complete(asyncio.sleep(1))
    timings = []
    iterations = int(os.environ.get("ITERATIONS", 10))
    concurrency = int(os.environ.get("CONCURRENCY", 100))
    final_results = []
    for i in range(iterations):
        session = ClientSession()
        futures = [ping(session, f"http://server/ping") for _ in range(concurrency)]

        start_time = time.time()
        ret_values = loop.run_until_complete(
            asyncio.gather(*futures, return_exceptions=True)
        )
        duration = time.time() - start_time
        for r in ret_values:
            final_results.append(r.status if type(r) is not Exception else None)

        loop.run_until_complete(session.close())
        logger.info(
            f"aiohttp={aiohttp.__version__} concurrency={concurrency} iteration={i:0>5} duration={duration}"
        )
        timings.append(duration)

    logger.info(
        f"aiohttp={aiohttp.__version__} concurrency={concurrency} iteration=MEAN duration={statistics.mean(timings)}"
    )
    logger.info(
        f"aiohttp={aiohttp.__version__} concurrency={concurrency} iteration=MIN duration={min(timings)}"
    )
    logger.info(
        f"aiohttp={aiohttp.__version__} concurrency={concurrency} iteration=MAX duration={max(timings)}"
    )
    try:
        logger.info(
            f"aiohttp={aiohttp.__version__} concurrency={concurrency} iteration=STDDEV duration={statistics.stdev(timings)}"
        )
    except:
        pass
    c = Counter(final_results)
    logger.info(
        f"aiohttp={aiohttp.__version__} concurrency={concurrency} iteration=STATUSES counter={c}"
    )

    loop.close()
    logger.info(f"Bye Bye!")
