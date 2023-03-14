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

    def get_all(self, pattern: str):
        results = self._r.keys(pattern)
        return [r.decode('utf-8') for r in results]

    def has(self, pattern: str) -> bool:
        return any(True for _ in self._r.scan_iter(pattern))

    def change_video_status(self, key: str, status_value: Literal['queued', 'in_progress', 'gathering', 'completed']):
        content = self[key]
        content['status'] = status_value
        self[key] = content

    def drop_statuses(self, default: Literal['queued', 'in_progress', 'gathering', 'completed'] = 'queued'):
        keys = self._r.keys('*')
        for key in keys:
            val = self[key]

            if isinstance(val, dict) and 'status' in val:
                val['status'] = default

            self[key] = val

    def subscribe(self, channel: str):
        p = self._r.pubsub()
        p.subscribe(channel)
        return p

    def publish(self, channel: str, message: str):
        self._r.publish(channel, message)


RedisConnection()
