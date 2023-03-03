import redis
import json

from typing import Literal


class RedisConnection:

    def __init__(self, host='127.0.0.1', port=6379, db_num=0):
        self._conn = redis.Redis(host=host, port=port, db=db_num)

    def __getitem__(self, item):
        return json.loads(self._conn.get(item))

    def __setitem__(self, key, value):
        self._conn.set(key, json.dumps(value))

    def change_video_status(self, key: str, status_value: Literal['queued', 'in_progress', 'failed', 'completed']):
        self._conn.set(key, status_value)


db = RedisConnection()
