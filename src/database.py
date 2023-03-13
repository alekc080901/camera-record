import json

import redis

from typing import Literal


class RedisConnection:
    """
    Подключение к базе данных Redis.
    """
    connection = None

    def __new__(cls, *args, **kwargs):
        if cls.connection is None:
            cls.connection = super().__new__(cls)
        return cls.connection

    def __init__(self, host='127.0.0.1', port=6379, db_num=0):
        self._r = redis.Redis(host=host, port=port, db=db_num)
        self._connection = self

    def __getitem__(self, item):
        return json.loads(self._r.get(item))

    def __setitem__(self, key, value):
        self._r.set(key, json.dumps(value))

    def has(self, pattern: str) -> bool:
        return any(True for _ in self._r.scan_iter(pattern))

    def change_video_status(self, key: str, status_value: Literal['queued', 'in_progress', 'gathering', 'completed']):
        self._r.set(key, status_value)

    def subscribe(self, channel: str):
        p = self._r.pubsub()
        p.subscribe(channel)
        return p

    def publish(self, channel: str, message: str):
        self._r.publish(channel, message)


RedisConnection()
