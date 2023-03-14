import asyncio

from datetime import datetime


async def until_async(date: datetime):
    """
    Pause your program until a specific end time.
    'time' is either a valid datetime object or unix timestamp in seconds (i.e. seconds since Unix epoch)
    """

    while datetime:
        now = date.now().timestamp()
        diff = date.timestamp() - now

        if diff <= 0:
            break
        else:
            await asyncio.sleep(diff / 2)
