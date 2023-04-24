import asyncio

from datetime import datetime


async def until_async(date: datetime):
    """
    Алгоритм асинхронного ожидания до указанной даты
    """

    while datetime:
        now = date.now().timestamp()
        diff = date.timestamp() - now

        if diff <= 0:
            break
        else:
            await asyncio.sleep(diff / 2)
